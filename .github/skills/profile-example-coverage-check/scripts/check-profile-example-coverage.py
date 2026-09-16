#!/usr/bin/env python3
"""Check whether IG examples exercise the constraints and slices a profile defines.

Reads the SUSHI-generated resources under igs/imaging-r4 and igs/imaging-r5,
derives a list of coverage targets from each profile (slices, mandatory
elements, fixed/pattern values, must-support flags, type constraints and
strong bindings), then resolves each target against every example that claims
conformance to the profile.

Targets whose slice discriminator cannot be evaluated statically (profile- and
type-based discriminators) are reported as UNVERIFIABLE rather than silently
passing or failing.
"""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

VERSIONS = OrderedDict([("4.0.1", ".")])

# Resource types that are IG machinery, never conformance examples.
NON_EXAMPLE_TYPES = {
    "StructureDefinition", "ValueSet", "CodeSystem", "ConceptMap",
    "CapabilityStatement", "ImplementationGuide", "SearchParameter",
    "OperationDefinition", "StructureMap", "NamingSystem",
}


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def resolve_fork_root(explicit):
    if explicit:
        return os.path.abspath(explicit)
    here = os.path.abspath(os.path.dirname(__file__))
    repo = here
    for _ in range(6):
        repo = os.path.dirname(repo)
        if os.path.isdir(os.path.join(repo, ".github", "skills")):
            break
    else:
        die("could not locate repository root; pass --fork-root")
    marker = os.path.join(repo, "current-branch.md")
    branch = None
    if os.path.isfile(marker):
        text = open(marker, encoding="utf-8").read()
        m = re.search(r"^\s*(?:[-*]\s*)?(?:branch\s*[:=]\s*)?([A-Za-z0-9._/-]+)\s*$",
                      text, re.MULTILINE | re.IGNORECASE)
        if m:
            branch = m.group(1).strip()
    candidates = []
    if branch:
        candidates.append(os.path.join(repo, f"hl7eu-imaging-fork-{branch}"))
    candidates.append(os.path.join(repo, "imaging-manifest-fork"))
    for c in candidates:
        if os.path.isdir(os.path.join(c, "fsh-generated", "resources")):
            return c
    die("could not locate imaging-manifest-fork; pass --fork-root")


def load_version(fork_root, folder):
    res_dir = os.path.join(fork_root, "fsh-generated", "resources")
    if not os.path.isdir(res_dir):
        return None
    out_dir = os.path.join(fork_root, "output")
    profiles, instances = {}, []
    missing_snapshot = []
    for fn in sorted(os.listdir(res_dir)):
        if not fn.endswith(".json"):
            continue
        try:
            data = json.load(open(os.path.join(res_dir, fn), encoding="utf-8"))
        except (ValueError, OSError):
            continue
        rt = data.get("resourceType")
        if rt == "StructureDefinition":
            if data.get("kind") == "resource" and data.get("derivation") == "constraint":
                # SUSHI emits differential only; slicing discriminators live in the
                # publisher-generated snapshot, so borrow it when available.
                if not data.get("snapshot"):
                    snap_file = os.path.join(out_dir, f"StructureDefinition-{data['id']}.json")
                    if os.path.isfile(snap_file):
                        try:
                            built = json.load(open(snap_file, encoding="utf-8"))
                            if built.get("snapshot"):
                                data["snapshot"] = built["snapshot"]
                        except (ValueError, OSError):
                            pass
                if not data.get("snapshot"):
                    missing_snapshot.append(data["id"])
                profiles[data["url"]] = data
        elif rt and rt not in NON_EXAMPLE_TYPES:
            instances.append((fn, data))
    return {"dir": res_dir, "profiles": profiles, "instances": instances,
            "missingSnapshot": missing_snapshot}


def iter_conformance_resources(resource):
    """Yield the resource plus nested Bundle entries and contained resources."""
    yield resource
    for entry in resource.get("entry", []) or []:
        inner = entry.get("resource")
        if isinstance(inner, dict):
            for r in iter_conformance_resources(inner):
                yield r
    for inner in resource.get("contained", []) or []:
        if isinstance(inner, dict):
            yield inner


def index_examples(instances):
    """Map profile canonical -> list of (source_file, resource)."""
    by_profile = {}
    for fn, root in instances:
        for res in iter_conformance_resources(root):
            for url in (res.get("meta") or {}).get("profile", []) or []:
                by_profile.setdefault(url.split("|")[0], []).append((fn, res))
    return by_profile


def build_reference_index(instances):
    """Index every resource by 'Type/id', by Bundle fullUrl and by '#containedId'."""
    index = {}
    for _fn, root in instances:
        for entry in root.get("entry", []) or []:
            res = entry.get("resource")
            if isinstance(res, dict) and entry.get("fullUrl"):
                index[entry["fullUrl"]] = res
        for res in iter_conformance_resources(root):
            rt, rid = res.get("resourceType"), res.get("id")
            if rt and rid:
                index.setdefault(f"{rt}/{rid}", res)
            if rid:
                index.setdefault(f"#{rid}", res)
    return index


def resolve_reference(ref, index):
    """Return the referenced resource, or None if it cannot be located."""
    if not isinstance(ref, dict):
        return None
    target = ref.get("reference")
    if not isinstance(target, str) or not target:
        return None
    if target in index:
        return index[target]
    tail = target.split("/")
    if len(tail) >= 2:
        return index.get(f"{tail[-2]}/{tail[-1]}")
    return None


def local_ancestry(profile, profiles):
    """Profile plus its ancestors that are defined inside this IG."""
    chain, seen = [], set()
    cur = profile
    while cur is not None and cur["url"] not in seen:
        seen.add(cur["url"])
        chain.append(cur)
        cur = profiles.get(cur.get("baseDefinition"))
    return chain


FIXED_RE = re.compile(r"^fixed[A-Z]")
PATTERN_RE = re.compile(r"^pattern[A-Z]")


def classify(elem):
    kinds = []
    if elem.get("sliceName"):
        kinds.append("slice")
    if (elem.get("min") or 0) >= 1:
        kinds.append("mandatory")
    if any(FIXED_RE.match(k) for k in elem):
        kinds.append("fixed")
    if any(PATTERN_RE.match(k) for k in elem):
        kinds.append("pattern")
    if elem.get("mustSupport"):
        kinds.append("must-support")
    for t in elem.get("type", []) or []:
        if t.get("profile") or t.get("targetProfile"):
            kinds.append("type-constraint")
            break
    b = elem.get("binding") or {}
    if b.get("strength") in ("required", "extensible") and (b.get("valueSet")):
        kinds.append("binding")
    return kinds


def collect_targets(profile, profiles, include_inherited):
    """Ordered map of element id -> {'kinds', 'origin'} for things examples should exercise."""
    targets = OrderedDict()
    sources = local_ancestry(profile, profiles) if include_inherited else [profile]
    for sd in reversed(sources):
        for elem in (sd.get("differential") or {}).get("element", []) or []:
            eid = elem.get("id")
            if not eid or "." not in eid:
                continue
            if eid.endswith(".url"):
                continue
            kinds = classify(elem)
            if not kinds:
                continue
            entry = targets.setdefault(eid, {"kinds": [], "origin": sd.get("name") or sd["id"]})
            for k in kinds:
                if k not in entry["kinds"]:
                    entry["kinds"].append(k)
    return targets


def snapshot_map(profile):
    return {e["id"]: e for e in (profile.get("snapshot") or {}).get("element", []) or []
            if e.get("id")}


def choice_keys(node, base):
    prefix = base[:-3]
    return [k for k in node if k.startswith(prefix) and len(k) > len(prefix)
            and k[len(prefix)].isupper()]


def get_children(node, name):
    if not isinstance(node, dict):
        return []
    if name.endswith("[x]"):
        out = []
        for k in choice_keys(node, name):
            v = node[k]
            out.extend(v if isinstance(v, list) else [v])
        return out
    v = node.get(name)
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def subset_match(expected, actual):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(k in actual and subset_match(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        return all(any(subset_match(e, a) for a in actual) for e in expected)
    return expected == actual


def expected_value(elem):
    for k, v in (elem or {}).items():
        if FIXED_RE.match(k) or PATTERN_RE.match(k):
            return v
    return None


def dig(node, path):
    """Follow a dotted discriminator path, returning candidate values.

    FHIRPath navigation markers ($this, resolve()) are dropped; reference
    resolution is handled by the caller.
    """
    parts = [p for p in (path or "").split(".")
             if p and p not in ("$this", "resolve()")]
    if not parts:
        return [node]
    cur = [node]
    for part in parts:
        nxt = []
        for c in cur:
            nxt.extend(get_children(c, part))
        cur = nxt
        if not cur:
            return []
    return cur


def relpath_keys(rel):
    """Turn a relative element-id fragment into JSON keys; choice slices use the slice name."""
    keys = []
    for seg in (rel or "").split("."):
        if not seg:
            continue
        name, _, slice_name = seg.partition(":")
        keys.append(slice_name if (slice_name and name.endswith("[x]")) else name)
    return keys


class Unverifiable(Exception):
    pass


def slice_matches(item, slice_id, snap, index):
    """True if item satisfies the slice's discriminators. Raises Unverifiable if undecidable."""
    parent_id = slice_id.rsplit(":", 1)[0]
    parent = snap.get(parent_id) or {}
    slice_elem = snap.get(slice_id) or {}
    discs = ((parent.get("slicing") or {}).get("discriminator")) or []

    base_name = parent_id.rsplit(".", 1)[-1]
    if base_name in ("extension", "modifierExtension"):
        urls = [t.get("profile", [None])[0] for t in slice_elem.get("type", []) or []
                if t.get("profile")]
        url_elem = snap.get(slice_id + ".url")
        ev = expected_value(url_elem)
        if ev:
            urls.append(ev)
        if urls:
            return isinstance(item, dict) and item.get("url") in [u for u in urls if u]
        raise Unverifiable("extension slice has no resolvable url")

    if not discs:
        raise Unverifiable("no discriminator on slicing")

    for d in discs:
        dtype = d.get("type")
        dpath = ".".join(p for p in (d.get("path") or "").split(".")
                         if p and p not in ("$this", "resolve()"))
        if dtype in ("value", "pattern"):
            target_id = f"{slice_id}.{dpath}" if dpath else slice_id
            exp = expected_value(snap.get(target_id))
            if exp is None:
                for cand_id, cand in snap.items():
                    if cand_id.startswith(target_id + ".") and expected_value(cand) is not None:
                        sub = cand_id[len(target_id) + 1:]
                        exp = {}
                        cursor = exp
                        parts = sub.split(".")
                        for p in parts[:-1]:
                            cursor[p] = {}
                            cursor = cursor[p]
                        cursor[parts[-1]] = expected_value(cand)
                        break
            if exp is None:
                raise Unverifiable(f"no fixed/pattern value at discriminator '{dpath}'")
            if not any(subset_match(exp, v) for v in dig(item, dpath)):
                return False
        elif dtype == "exists":
            present = bool(dig(item, dpath))
            want = (slice_elem.get("min") or 0) >= 1
            child = snap.get(f"{slice_id}.{dpath}" if dpath else slice_id)
            if child is not None:
                want = (child.get("min") or 0) >= 1
                if child.get("max") == "0":
                    want = False
            if present != want:
                return False
        elif dtype == "type":
            sn = slice_elem.get("sliceName") or ""
            if base_name.endswith("[x]") and sn:
                raise Unverifiable("type discriminator on choice handled by key name")
            raise Unverifiable("type discriminator not statically evaluable")
        elif dtype == "profile":
            # The target profile may sit on the discriminator element itself or on a
            # descendant (e.g. suspectEntity:procedure.instance only Reference(X)).
            cands = []
            bases = []
            if dpath:
                bases.append((f"{slice_id}.{dpath}", relpath_keys(dpath)))
            bases.append((slice_id, []))
            for base_id, prefix in bases:
                for cid, cel in snap.items():
                    if cid != base_id and not cid.startswith(base_id + "."):
                        continue
                    wanted = set()
                    for t in cel.get("type", []) or []:
                        wanted.update(t.get("targetProfile") or [])
                        wanted.update(t.get("profile") or [])
                    if wanted:
                        cands.append((prefix + relpath_keys(cid[len(base_id):]), wanted))
                if cands:
                    break
            if not cands:
                raise Unverifiable("profile discriminator with no declared target profile")
            matched, resolvable = False, False
            for keys, wanted in cands:
                nodes = [item]
                for k in keys:
                    nodes = [c for n in nodes for c in get_children(n, k)]
                for cand in nodes:
                    if not isinstance(cand, dict):
                        continue
                    resolvable = True
                    target = cand if cand.get("resourceType") else resolve_reference(cand, index)
                    if target is None:
                        raise Unverifiable("reference target not found among examples")
                    declared = {u.split("|")[0]
                                for u in (target.get("meta") or {}).get("profile", []) or []}
                    if declared & wanted:
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                return False
        else:
            raise Unverifiable(f"{dtype} discriminator not statically evaluable")
    return True


def resolve(nodes, segments, cur_id, snap, index):
    """Resolve element-id segments against instance nodes. Returns (nodes, unverifiable_reason)."""
    if not segments:
        return nodes, None
    seg, rest = segments[0], segments[1:]
    name, _, slice_name = seg.partition(":")
    next_id = f"{cur_id}.{name}" + (f":{slice_name}" if slice_name else "")
    out = []
    for node in nodes:
        if slice_name and name.endswith("[x]"):
            v = node.get(slice_name) if isinstance(node, dict) else None
            if v is not None:
                out.extend(v if isinstance(v, list) else [v])
            continue
        candidates = get_children(node, name)
        if not slice_name:
            out.extend(candidates)
            continue
        for item in candidates:
            try:
                if slice_matches(item, next_id, snap, index):
                    out.append(item)
            except Unverifiable as exc:
                return [], str(exc)
    return resolve(out, rest, next_id, snap, index)


def is_populated(node):
    if node is None:
        return False
    if isinstance(node, (dict, list)):
        return len(node) > 0
    if isinstance(node, str):
        return node != ""
    return True


def evaluate(profile, targets, examples, index):
    snap = snapshot_map(profile)
    root = profile.get("type") or profile["id"]
    covered, uncovered, unverifiable = [], [], []
    for eid, meta in targets.items():
        segments = eid.split(".")[1:]
        if not segments:
            continue
        hit, reason = False, None
        for _fn, res in examples:
            nodes, why = resolve([res], segments, root, snap, index)
            if why:
                reason = why
                continue
            if any(is_populated(n) for n in nodes):
                hit = True
                break
        if hit:
            covered.append((eid, meta))
        elif reason:
            unverifiable.append((eid, meta, reason))
        else:
            uncovered.append((eid, meta))
    return covered, uncovered, unverifiable


def report(version, profile, examples, covered, uncovered, unverifiable, verbose):
    name = profile.get("name") or profile["id"]
    total = len(covered) + len(uncovered) + len(unverifiable)
    pct = (100.0 * len(covered) / total) if total else 100.0
    print(f"\n### [{version}] {name}")
    print(f"    profile   : {profile['url']}")
    if not examples:
        print("    examples  : NONE — no instance declares conformance to this profile")
    else:
        shown = sorted({fn for fn, _ in examples})
        print(f"    examples  : {len(examples)} instance(s) in {len(shown)} file(s)")
        if verbose:
            for fn in shown:
                print(f"                - {fn}")
    print(f"    coverage  : {len(covered)}/{total} targets ({pct:.0f}%)"
          f"  uncovered={len(uncovered)}  unverifiable={len(unverifiable)}")
    if uncovered:
        print("    UNCOVERED:")
        for eid, meta in uncovered:
            print(f"      - {eid}  [{', '.join(meta['kinds'])}]  (from {meta['origin']})")
    if unverifiable and verbose:
        print("    UNVERIFIABLE:")
        for eid, meta, why in unverifiable:
            print(f"      - {eid}  [{', '.join(meta['kinds'])}]  ({why})")
    return len(uncovered)


def main():
    ap = argparse.ArgumentParser(description="Check example coverage of profile constraints.")
    ap.add_argument("profile", nargs="?", default="--all",
                    help="profile name or id (default: all profiles)")
    ap.add_argument("--all", action="store_true", help="check every profile in the IG")
    ap.add_argument("--version", choices=["4.0.1", "5.0.0", "all"], default="all")
    ap.add_argument("--fork-root", help="path to the fork worktree containing igs/")
    ap.add_argument("--include-inherited", action="store_true",
                    help="also require coverage of constraints inherited from IG-local parents")
    ap.add_argument("--include-obligations", action="store_true",
                    help="include *Obligation* overlay profiles, which normally have no instances")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="list example files and unverifiable targets")
    ap.add_argument("--json", dest="as_json", action="store_true", help="emit JSON")
    ap.add_argument("--warn-only", action="store_true", help="always exit 0")
    args = ap.parse_args()

    want_all = args.all or args.profile == "--all"
    fork_root = resolve_fork_root(args.fork_root)
    versions = list(VERSIONS) if args.version == "all" else [args.version]

    total_uncovered, checked, results = 0, 0, []
    for ver in versions:
        data = load_version(fork_root, VERSIONS[ver])
        if data is None:
            print(f"WARNING: no generated resources for {ver}; run the IG build first",
                  file=sys.stderr)
            continue
        by_profile = index_examples(data["instances"])
        ref_index = build_reference_index(data["instances"])
        if data.get("missingSnapshot"):
            print(f"WARNING: {len(data['missingSnapshot'])} profile(s) in {ver} have no "
                  f"snapshot; run the IG build so slices can be evaluated", file=sys.stderr)
        selected = []
        for url, sd in sorted(data["profiles"].items(), key=lambda kv: kv[1].get("name", "")):
            named = args.profile in (sd.get("name"), sd.get("id"), url)
            if want_all and not args.include_obligations and "obligation" in (
                    sd.get("name") or sd["id"]).lower():
                continue
            if want_all or named:
                selected.append((url, sd))
        if not selected:
            print(f"WARNING: profile '{args.profile}' not found in {ver}", file=sys.stderr)
            continue
        for url, sd in selected:
            targets = collect_targets(sd, data["profiles"], args.include_inherited)
            examples = by_profile.get(url, [])
            cov, unc, unv = evaluate(sd, targets, examples, ref_index)
            checked += 1
            total_uncovered += len(unc)
            if args.as_json:
                results.append({
                    "version": ver, "profile": sd.get("name"), "url": url,
                    "examples": sorted({fn for fn, _ in examples}),
                    "covered": [e for e, _ in cov],
                    "uncovered": [{"id": e, "kinds": m["kinds"], "origin": m["origin"]}
                                  for e, m in unc],
                    "unverifiable": [{"id": e, "kinds": m["kinds"], "reason": w}
                                     for e, m, w in unv],
                })
            else:
                report(ver, sd, examples, cov, unc, unv, args.verbose)

    if args.as_json:
        print(json.dumps({"forkRoot": fork_root, "results": results}, indent=2))
    else:
        print(f"\n=== {checked} profile check(s); {total_uncovered} uncovered target(s) ===")
    return 0 if (args.warn_only or total_uncovered == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
