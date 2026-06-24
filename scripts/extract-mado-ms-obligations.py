#!/usr/bin/env python3
"""
Step 1-9: Extract IHE-MADO, EU imaging-manifest, XtEHR EHDS, and merged field inventories.
Step 7 adds DICOM KOS mappings from mapping.csv.
Step 8 enriches mapping data with XtEHR model mappings from xtehr-model-mapping.csv.
Step 9 produces final merged inventory.
"""

import csv
import glob
import json
import os
import re
import sys
from collections import OrderedDict

# Configuration
SUSHI_CONFIG = 'imaging-manifest-fork/sushi-config.yaml'
IHE_PACKAGE_ID = 'ihe.rad.mado'
IHE_PACKAGE_DEFAULT_VERSION = 'current'
XTE_DIR = os.path.expanduser('~/.fhir/packages/xtehr.eu.ehds.models#1.0.0/package')
OUT_DIR = 'imaging-manifest-fork/output'
OUT_CSV_IHE = 'ai-result/step1-ihe-mado-fields.csv'
OUT_CSV_EU = 'ai-result/step2-eu-mado.csv'
OUT_CSV_EHDS = 'ai-result/step3-ehds-fields.csv'
OUT_CSV_ALL = 'ai-result/step4-ihe-eu-mado-fields.csv'
OUT_CSV_FINAL = 'ai-result/step5-ihe-eu-mado-ehds-fields.csv'
OUT_CSV_STEP6 = 'ai-result/step6-all-fields.csv'
OUT_CSV_STEP7 = 'ai-result/step7-mapping.csv'
OUT_CSV_STEP8 = 'ai-result/step8-xtehr-enriched.csv'
OUT_CSV_STEP9 = 'ai-result/step9-all.csv'
MAPPING_CSV = 'imaging-manifest-fork/input/mapping/mapping.csv'
XTEHR_MODEL_MAPPING_CSV = 'imaging-manifest-fork/input/mapping/xtehr-model-mapping.csv'

# XtEHR Actor URIs
XTE_CONSUMER = 'https://www.xt-ehr.eu/specifications/fhir/actor-consumer'
XTE_PRODUCER = 'https://www.xt-ehr.eu/specifications/fhir/actor-producer'

# EU imaging-manifest Actor URIs
EU_CONSUMER = 'http://hl7.eu/fhir/imaging-manifest/ActorDefinition/EuMadoImagingManifestConsumer'
EU_PRODUCER = 'http://hl7.eu/fhir/imaging-manifest/ActorDefinition/EuMadoImagingManifestProducer'

EHDS_REF_PATTERN = r'\bEHDS[A-Za-z0-9]+(?:\.[A-Za-z0-9\[\]x-]+)+\b'


def resolve_ihe_dir_from_sushi_config():
    """Resolve ihe.rad.mado package directory using sushi-config dependency version."""
    version = IHE_PACKAGE_DEFAULT_VERSION

    try:
        with open(SUSHI_CONFIG, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match typical inline form under dependencies:
        # ihe.rad.mado: dev
        dep_match = re.search(
            r'(?ms)^dependencies:\s*$.*?^\s*' + re.escape(IHE_PACKAGE_ID) + r'\s*:\s*([^\n#]+)',
            content,
        )
        if dep_match:
            value = dep_match.group(1).strip().strip('"\'')
            # Ignore object-mapping starts and fall back if unresolved.
            if value and value not in {'|', '>', '{'}:
                version = value
    except Exception as e:
        print(
            f'Warning: Could not parse {SUSHI_CONFIG} for {IHE_PACKAGE_ID}: {e}. Using {IHE_PACKAGE_DEFAULT_VERSION}.',
            file=sys.stderr,
        )

    ihe_dir = os.path.expanduser(f'~/.fhir/packages/{IHE_PACKAGE_ID}#{version}/package')
    if not os.path.isdir(ihe_dir):
        fallback = os.path.expanduser(f'~/.fhir/packages/{IHE_PACKAGE_ID}#{IHE_PACKAGE_DEFAULT_VERSION}/package')
        print(
            f'Warning: Resolved IHE package path not found: {ihe_dir}. Falling back to {fallback}.',
            file=sys.stderr,
        )
        ihe_dir = fallback

    return ihe_dir


def deduplicate_rows(rows):
    """Return list with duplicate rows removed (preserves first occurrence order)."""
    seen = set()
    result = []
    for row in rows:
        key = tuple(row.values())
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def get_profile_name(url):
    """Extract profile name from canonical URL."""
    if not url:
        return ''
    return url.split('/')[-1]


def extract_obligations(element, consumer_actor, producer_actor):
    """Extract consumer/producer obligation codes and an optional requirement string."""
    consumer_obl = ''
    producer_obl = ''
    requirement_docs = []

    for ext in (element.get('extension', []) or []):
        if ext.get('url') != 'http://hl7.org/fhir/StructureDefinition/obligation':
            continue

        actor = ''
        code = ''
        documentation = ''

        for sub in (ext.get('extension', []) or []):
            if sub.get('url') == 'actor':
                actor = sub.get('valueCanonical', '')
            elif sub.get('url') == 'code':
                code = sub.get('valueCode', '')
            elif sub.get('url') == 'documentation':
                documentation = sub.get('valueMarkdown', '')

        if code:
            if actor == consumer_actor:
                consumer_obl = code
            elif actor == producer_actor:
                producer_obl = code

        if documentation and documentation not in requirement_docs:
            requirement_docs.append(documentation)

    return consumer_obl, producer_obl, ' | '.join(requirement_docs)


def extract_ehds_references(text, ehds_lookup):
    """Extract unique EHDS references mentioned in documentation text."""
    if not text:
        return ''

    refs = []
    seen = set()
    for candidate in re.findall(EHDS_REF_PATTERN, text):
        lookup_candidates = [candidate]
        normalized_candidate = re.sub(r'\[[^\]]+\]', '[x]', candidate)
        if normalized_candidate != candidate:
            lookup_candidates.append(normalized_candidate)

        for lookup_candidate in lookup_candidates:
            if lookup_candidate in ehds_lookup and lookup_candidate not in seen:
                refs.append(lookup_candidate)
                seen.add(lookup_candidate)
                break

    return ' | '.join(refs)


def _normalize_ihe_key_for_match(key):
    """Normalize IHE cross-reference key for tolerant matching.

    Keeps the profile/path structure but normalizes bracketed slice names by
    removing dashes/underscores and lowercasing (e.g. retrieve-location-uid
    and retrieveLocationUid become equivalent).
    """
    if not key:
        return ''

    def repl(match):
        raw = match.group(1)
        normalized = re.sub(r'[-_\s]', '', raw).lower()
        return f'[{normalized}]'

    return re.sub(r'\[([^\]]+)\]', repl, key.strip())


def _slice_names(key):
    """Extract ordered slice names from a cross-reference key."""
    if not key:
        return []
    return re.findall(r'\[([^\]]+)\]', key)


def _is_camel_vs_kebab_slice_mismatch(left_key, right_key):
    """True when keys are normalization-equivalent but differ by camelCase vs kebab-case slice names."""
    if not left_key or not right_key:
        return False
    if _normalize_ihe_key_for_match(left_key) != _normalize_ihe_key_for_match(right_key):
        return False

    left_slices = _slice_names(left_key)
    right_slices = _slice_names(right_key)
    if len(left_slices) != len(right_slices):
        return False

    for l_slice, r_slice in zip(left_slices, right_slices):
        l_has_kebab = '-' in l_slice
        r_has_kebab = '-' in r_slice
        l_has_camel = bool(re.search(r'[A-Z]', l_slice))
        r_has_camel = bool(re.search(r'[A-Z]', r_slice))

        if (l_has_kebab and r_has_camel) or (r_has_kebab and l_has_camel):
            return True

    return False


def load_xtehr_model_mappings():
    """Load XtEHR model mappings from xtehr-model-mapping.csv.
    
    Returns dict: XtEHR class name -> { XtEHR field -> { 'eu_resource': str, 'eu_field': str } }
    """
    mappings = {}
    if not os.path.isfile(XTEHR_MODEL_MAPPING_CSV):
        print(f'Warning: XtEHR model mapping file {XTEHR_MODEL_MAPPING_CSV} not found.', file=sys.stderr)
        return mappings
    
    try:
        # Try UTF-8 first, fall back to Latin-1 if that fails
        try:
            with open(XTEHR_MODEL_MAPPING_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    xtehr_class = row.get('XtEHR Class', '').strip()
                    xtehr_field = row.get('XtEHR field', '').strip()
                    eu_resource = row.get('EuMado resource', '').strip()
                    eu_field = row.get('EuMado field', '').strip()
                    
                    # Skip empty rows or rows without XtEHR class
                    if not xtehr_class or not xtehr_field:
                        continue
                    
                    if xtehr_class not in mappings:
                        mappings[xtehr_class] = {}
                    
                    # Store mapping as dict for this field
                    mappings[xtehr_class][xtehr_field] = {
                        'eu_resource': eu_resource,
                        'eu_field': eu_field,
                    }
        except UnicodeDecodeError:
            # Fall back to Latin-1 encoding
            print(f'Note: Retrying {XTEHR_MODEL_MAPPING_CSV} with Latin-1 encoding', file=sys.stderr)
            with open(XTEHR_MODEL_MAPPING_CSV, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    xtehr_class = row.get('XtEHR Class', '').strip()
                    xtehr_field = row.get('XtEHR field', '').strip()
                    eu_resource = row.get('EuMado resource', '').strip()
                    eu_field = row.get('EuMado field', '').strip()
                    
                    # Skip empty rows or rows without XtEHR class
                    if not xtehr_class or not xtehr_field:
                        continue
                    
                    if xtehr_class not in mappings:
                        mappings[xtehr_class] = {}
                    
                    # Store mapping as dict for this field
                    mappings[xtehr_class][xtehr_field] = {
                        'eu_resource': eu_resource,
                        'eu_field': eu_field,
                    }
    except Exception as e:
        print(f'Warning: Failed to load {XTEHR_MODEL_MAPPING_CSV}: {e}', file=sys.stderr)
    
    return mappings


def main():
    """Main extraction workflow for the sequential four-step CSV extraction."""
    ihe_dir = resolve_ihe_dir_from_sushi_config()
    print(f'Using IHE package directory: {ihe_dir}')
    
    # ===== STEP 1: Load all IHE-MADO profiles =====
    ihe_profiles_by_url = {}
    ihe_profiles_by_name = {}
    for p in sorted(glob.glob(os.path.join(ihe_dir, 'StructureDefinition-*.json'))):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('resourceType') == 'StructureDefinition' and data.get('url'):
                prof_name = get_profile_name(data['url'])
                ihe_profiles_by_url[data['url']] = data
                ihe_profiles_by_name[prof_name] = data
        except Exception as e:
            print(f'Warning: Failed to load IHE profile {p}: {e}', file=sys.stderr)
    
    # Generate ihe-mado-fields.csv
    ihe_rows = []
    for prof_name in sorted(ihe_profiles_by_name.keys()):
        sd = ihe_profiles_by_name[prof_name]
        for el in (sd.get('snapshot', {}).get('element', []) or []):
            elem_path = el.get('path', '')
            if not elem_path or '.' not in elem_path:
                continue
            
            # Extract field path (everything after the profile name dot)
            # elem_path format: ProfileName.path.to.element
            # We want: path.to.element
            parts = elem_path.split('.')
            if len(parts) > 1:
                field_path = '.'.join(parts[1:])
                # Append slice name if present
                if el.get('sliceName'):
                    field_path = f"{field_path}[{el.get('sliceName')}]"
            else:
                continue
            
            is_ms = 'MS' if el.get('mustSupport') is True else ''
            
            ihe_rows.append(OrderedDict([
                ('Profile', prof_name),
                ('Field', field_path),
                ('MS', is_ms),
            ]))
    
    # Write IHE-MADO CSV
    ihe_rows = deduplicate_rows(ihe_rows)
    os.makedirs(os.path.dirname(OUT_CSV_IHE), exist_ok=True)
    with open(OUT_CSV_IHE, 'w', newline='', encoding='utf-8') as f:
        if ihe_rows:
            w = csv.DictWriter(f, fieldnames=['Profile', 'Field', 'MS'])
            w.writeheader()
            w.writerows(ihe_rows)
    
    print(f'WROTE {OUT_CSV_IHE} rows={len(ihe_rows)}')
    
    # ===== STEP 2: Load all EU imaging-manifest profiles =====
    eu_profiles_by_url = {}
    eu_profiles_by_name = {}
    for p in sorted(glob.glob(os.path.join(OUT_DIR, 'StructureDefinition-EuMado*.json'))):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('resourceType') == 'StructureDefinition' and data.get('url'):
                prof_name = get_profile_name(data['url'])
                eu_profiles_by_url[data['url']] = data
                eu_profiles_by_name[prof_name] = data
        except Exception as e:
            print(f'Warning: Failed to load EU profile {p}: {e}', file=sys.stderr)
    
    # Generate eu-mado.csv with IHE-MADO cross-references and obligations
    eu_rows = []
    for eu_url in sorted(eu_profiles_by_url.keys()):
        eu_sd = eu_profiles_by_url[eu_url]
        eu_name = get_profile_name(eu_url)
        
        # Get the base IHE profile if available
        base_url = eu_sd.get('baseDefinition', '')
        base_ihe_name = get_profile_name(base_url) if base_url else ''
        
        for el in (eu_sd.get('snapshot', {}).get('element', []) or []):
            elem_path = el.get('path', '')
            if not elem_path or '.' not in elem_path:
                continue
            
            # Extract field path (everything after the profile name dot)
            # elem_path format: ProfileName.path.to.element
            # We want: path.to.element
            parts = elem_path.split('.')
            if len(parts) > 1:
                field_path = '.'.join(parts[1:])
                # Append slice name if present
                if el.get('sliceName'):
                    field_path = f"{field_path}[{el.get('sliceName')}]"
            else:
                continue
            
            is_ms = 'MS' if el.get('mustSupport') is True else ''
            consumer_obl, producer_obl, obligation_req = extract_obligations(el, EU_CONSUMER, EU_PRODUCER)
            
            # Build IHE-MADO cross-reference (profile.field format)
            ihe_cross_ref = f"{base_ihe_name}.{field_path}" if base_ihe_name else ''
            
            eu_rows.append(OrderedDict([
                ('Profile', eu_name),
                ('Field', field_path),
                ('MS', is_ms),
                ('IHE-MADO', ihe_cross_ref),
                ('Consumer', consumer_obl),
                ('Producer', producer_obl),
                ('Documentation', obligation_req),
            ]))
    
    # Write EU-MADO CSV
    eu_rows = deduplicate_rows(eu_rows)
    os.makedirs(os.path.dirname(OUT_CSV_EU), exist_ok=True)
    with open(OUT_CSV_EU, 'w', newline='', encoding='utf-8') as f:
        if eu_rows:
            w = csv.DictWriter(f, fieldnames=['Profile', 'Field', 'MS', 'IHE-MADO', 'Consumer', 'Producer', 'Documentation'])
            w.writeheader()
            w.writerows(eu_rows)
    
    print(f'WROTE {OUT_CSV_EU} rows={len(eu_rows)}')
    
    # ===== STEP 3: Load all XtEHR EHDS profiles with obligations =====
    ehds_base_profiles = {}
    for p in sorted(glob.glob(os.path.join(XTE_DIR, 'StructureDefinition-EHDS*.json'))):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('resourceType') == 'StructureDefinition':
                name = data.get('name', '')
                # Only load base EHDS profiles, not Obligations profiles
                if name and name.startswith('EHDS') and not name.endswith('Obligations'):
                    ehds_base_profiles[name] = data
        except Exception as e:
            print(f'Warning: Failed to load EHDS profile {p}: {e}', file=sys.stderr)
    
    # Load XtEHR Obligations profiles
    ehds_obligations_by_name = {}
    for p in sorted(glob.glob(os.path.join(XTE_DIR, 'StructureDefinition-*.json'))):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('resourceType') == 'StructureDefinition':
                name = data.get('name', '')
                if name and name.endswith('Obligations'):
                    base_name = name[:-11]  # Remove "Obligations" suffix
                    ehds_obligations_by_name[base_name] = data
        except Exception as e:
            print(f'Warning: Failed to load obligations profile {p}: {e}', file=sys.stderr)
    
    # Generate ehds-fields.csv with obligations
    ehds_rows = []
    for ehds_name in sorted(ehds_base_profiles.keys()):
        ehds_sd = ehds_base_profiles[ehds_name]
        obls_sd = ehds_obligations_by_name.get(ehds_name)
        
        for el in (ehds_sd.get('snapshot', {}).get('element', []) or []):
            elem_path = el.get('path', '')
            elem_id = el.get('id', '')
            if not elem_path or '.' not in elem_path:
                continue
            
            is_ms = 'MS' if el.get('mustSupport') is True else ''
            
            # Extract obligations for this element
            consumer_obl = ''
            producer_obl = ''
            
            if obls_sd:
                for obls_el in (obls_sd.get('snapshot', {}).get('element', []) or []):
                    if obls_el.get('id') == elem_id:
                        # Extract obligations from extension
                        for ext in obls_el.get('extension', []):
                            if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/obligation':
                                actor = ''
                                code = ''
                                for sub in ext.get('extension', []):
                                    if sub.get('url') == 'actor':
                                        actor = sub.get('valueCanonical', '')
                                    if sub.get('url') == 'code':
                                        code = sub.get('valueCode', '')
                                
                                if code:
                                    if actor == XTE_CONSUMER:
                                        consumer_obl = code
                                    elif actor == XTE_PRODUCER:
                                        producer_obl = code
                        break
            
            # Extract field path (everything after the profile name dot)
            # elem_path format: ProfileName.path.to.element
            # We want: path.to.element
            parts = elem_path.split('.')
            if len(parts) > 1:
                field_path = '.'.join(parts[1:])
                # Append slice name if present
                if el.get('sliceName'):
                    field_path = f"{field_path}[{el.get('sliceName')}]"
            else:
                continue
            
            ehds_rows.append(OrderedDict([
                ('Profile', ehds_name),
                ('Field', field_path),
                ('Cross-reference', elem_path),
                ('MS', is_ms),
                ('Consumer', consumer_obl),
                ('Producer', producer_obl),
            ]))
    
    # Write EHDS CSV
    ehds_rows = deduplicate_rows(ehds_rows)
    os.makedirs(os.path.dirname(OUT_CSV_EHDS), exist_ok=True)
    with open(OUT_CSV_EHDS, 'w', newline='', encoding='utf-8') as f:
        if ehds_rows:
            w = csv.DictWriter(f, fieldnames=['Profile', 'Field', 'Cross-reference', 'MS', 'Consumer', 'Producer'])
            w.writeheader()
            w.writerows(ehds_rows)
    
    print(f'WROTE {OUT_CSV_EHDS} rows={len(ehds_rows)}')
    
    # ===== STEP 4: Merge IHE-MADO and EU-MADO profiles =====
    # Load IHE-MADO fields into a dict keyed by "Profile.Field"
    ihe_by_key = {}
    with open(OUT_CSV_IHE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['Profile']}.{row['Field']}"
            ihe_by_key[key] = row
    ihe_norm_to_keys = {}
    for key in ihe_by_key:
        norm = _normalize_ihe_key_for_match(key)
        ihe_norm_to_keys.setdefault(norm, []).append(key)
    
    # Load EU-MADO fields
    eu_rows_from_file = []
    with open(OUT_CSV_EU, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eu_rows_from_file.append(row)
    
    # Merge IHE and EU rows
    merged_rows = []
    matched_ihe_keys = set()
    
    for eu_row in eu_rows_from_file:
        ihe_cross_ref = eu_row.get('IHE-MADO', '')
        eu_profile = eu_row.get('Profile', '')
        eu_field = eu_row.get('Field', '')
        eu_cross_ref = f'{eu_profile}.{eu_field}' if eu_profile and eu_field else ''
        eu_ms = eu_row.get('MS', '')
        eu_consumer = eu_row.get('Consumer', '')
        eu_producer = eu_row.get('Producer', '')
        eu_documentation = eu_row.get('Documentation', '')
        
        if ihe_cross_ref and ihe_cross_ref in ihe_by_key:
            # Found a match
            ihe_row = ihe_by_key[ihe_cross_ref]
            ihe_ms = ihe_row.get('MS', '')
            matched_ihe_keys.add(ihe_cross_ref)
            
            # Merge MS: if either has MS, mark as MS
            combined_ms = 'MS' if (ihe_ms == 'MS' or eu_ms == 'MS') else ''
            
            merged_rows.append(OrderedDict([
                ('IHE-MADO', ihe_cross_ref),
                ('EU-MADO', eu_cross_ref),
                ('MS', combined_ms),
                ('Consumer', eu_consumer),
                ('Producer', eu_producer),
                ('Documentation', eu_documentation),
            ]))
        else:
            # Warn on likely root-cause mismatch: kebab-case vs camelCase slice naming.
            if ihe_cross_ref:
                norm = _normalize_ihe_key_for_match(ihe_cross_ref)
                for candidate in ihe_norm_to_keys.get(norm, []):
                    if _is_camel_vs_kebab_slice_mismatch(ihe_cross_ref, candidate):
                        print(
                            f"WARNING Step4 slice-name mismatch (camelCase vs kebab-case): "
                            f"EU IHE-MADO cross-ref '{ihe_cross_ref}' vs IHE key '{candidate}'.",
                            file=sys.stderr,
                        )
                        break
            # EU row with no matching IHE base
            merged_rows.append(OrderedDict([
                ('IHE-MADO', ''),
                ('EU-MADO', eu_cross_ref),
                ('MS', eu_ms),
                ('Consumer', eu_consumer),
                ('Producer', eu_producer),
                ('Documentation', eu_documentation),
            ]))
    
    # Add remaining IHE rows that weren't matched
    for key, ihe_row in ihe_by_key.items():
        if key not in matched_ihe_keys:
            ihe_ms = ihe_row.get('MS', '')
            merged_rows.append(OrderedDict([
                ('IHE-MADO', key),
                ('EU-MADO', ''),
                ('MS', ihe_ms),
                ('Consumer', ''),
                ('Producer', ''),
                ('Documentation', ''),
            ]))
    
    # Write merged CSV
    merged_rows = deduplicate_rows(merged_rows)
    os.makedirs(os.path.dirname(OUT_CSV_ALL), exist_ok=True)
    with open(OUT_CSV_ALL, 'w', newline='', encoding='utf-8') as f:
        if merged_rows:
            w = csv.DictWriter(f, fieldnames=['IHE-MADO', 'EU-MADO', 'MS', 'Consumer', 'Producer', 'Documentation'])
            w.writeheader()
            w.writerows(merged_rows)
    
    print(f'WROTE {OUT_CSV_ALL} rows={len(merged_rows)}')

    # ===== STEP 5: Add EHDS cross-references based on documentation text =====
    # Build EHDS lookup: cross-reference -> (Consumer, Producer)
    ehds_lookup = set()
    ehds_obligations_lookup = {}
    with open(OUT_CSV_EHDS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            field_ref = row.get('Cross-reference', '') or row.get('Field', '')
            if field_ref:
                ehds_lookup.add(field_ref)
                ehds_obligations_lookup[field_ref] = (
                    row.get('Consumer', ''),
                    row.get('Producer', '')
                )

    def get_ehds_obligations(ehds_refs_str, ehds_obligations_lookup):
        """Extract Consumer and Producer obligations for EHDS references."""
        if not ehds_refs_str:
            return '', ''
        # EHDS column can contain multiple references separated by '; '
        refs = [r.strip() for r in ehds_refs_str.split('; ') if r.strip()]
        consumer_codes = []
        producer_codes = []
        for ref in refs:
            if ref in ehds_obligations_lookup:
                consumer, producer = ehds_obligations_lookup[ref]
                if consumer:
                    consumer_codes.append(consumer)
                if producer:
                    producer_codes.append(producer)
        return '; '.join(consumer_codes), '; '.join(producer_codes)

    final_rows = []
    with open(OUT_CSV_ALL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            documentation = row.get('Documentation', '')
            ehds_refs = extract_ehds_references(documentation, ehds_lookup)
            ehds_consumer, ehds_producer = get_ehds_obligations(ehds_refs, ehds_obligations_lookup)
            final_rows.append(OrderedDict([
                ('IHE-MADO', row.get('IHE-MADO', '')),
                ('EU-MADO', row.get('EU-MADO', '')),
                ('MS', row.get('MS', '')),
                ('Consumer', row.get('Consumer', '')),
                ('Producer', row.get('Producer', '')),
                ('Documentation', documentation),
                ('EHDS', ehds_refs),
                ('EHDS-Consumer', ehds_consumer),
                ('EHDS-Producer', ehds_producer),
            ]))

    final_rows = deduplicate_rows(final_rows)
    with open(OUT_CSV_FINAL, 'w', newline='', encoding='utf-8') as f:
        if final_rows:
            w = csv.DictWriter(f, fieldnames=['IHE-MADO', 'EU-MADO', 'MS', 'Consumer', 'Producer', 'Documentation', 'EHDS', 'EHDS-Consumer', 'EHDS-Producer'])
            w.writeheader()
            w.writerows(final_rows)

    print(f'WROTE {OUT_CSV_FINAL} rows={len(final_rows)}')

    # ===== STEP 6: Add EHDS-only fields (not mapped to IHE/EU) =====
    # Collect all EHDS cross-references already in step 5
    ehds_covered = set()
    with open(OUT_CSV_FINAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ehds_str = row.get('EHDS', '')
            if ehds_str:
                # EHDS column can contain multiple references separated by '; '
                for ref in ehds_str.split('; '):
                    ref = ref.strip()
                    if ref:
                        ehds_covered.add(ref)

    # Read all EHDS fields from step 3
    ehds_all_fields = []
    with open(OUT_CSV_EHDS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cross_ref = row.get('Cross-reference', '')
            if cross_ref:
                ehds_all_fields.append(cross_ref)

    # Find unmapped EHDS fields
    unmapped_ehds_refs = [ref for ref in ehds_all_fields if ref not in ehds_covered]

    # Build step 6 output: all step 5 rows + new unmapped EHDS rows
    step6_rows = []
    
    # Add all step 5 rows
    with open(OUT_CSV_FINAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            step6_rows.append(OrderedDict([
                ('IHE-MADO', row.get('IHE-MADO', '')),
                ('EU-MADO', row.get('EU-MADO', '')),
                ('MS', row.get('MS', '')),
                ('Consumer', row.get('Consumer', '')),
                ('Producer', row.get('Producer', '')),
                ('Documentation', row.get('Documentation', '')),
                ('EHDS', row.get('EHDS', '')),
                ('EHDS-Consumer', row.get('EHDS-Consumer', '')),
                ('EHDS-Producer', row.get('EHDS-Producer', '')),
            ]))
    
    # Add new rows for unmapped EHDS fields
    for ehds_ref in unmapped_ehds_refs:
        # Look up obligations for this unmapped EHDS field
        ehds_consumer, ehds_producer = '', ''
        if ehds_ref in ehds_obligations_lookup:
            ehds_consumer, ehds_producer = ehds_obligations_lookup[ehds_ref]
        
        step6_rows.append(OrderedDict([
            ('IHE-MADO', ''),
            ('EU-MADO', ''),
            ('MS', ''),
            ('Consumer', ''),
            ('Producer', ''),
            ('Documentation', ''),
            ('EHDS', ehds_ref),
            ('EHDS-Consumer', ehds_consumer),
            ('EHDS-Producer', ehds_producer),
        ]))

    # Write step 6 CSV
    step6_rows = deduplicate_rows(step6_rows)
    with open(OUT_CSV_STEP6, 'w', newline='', encoding='utf-8') as f:
        if step6_rows:
            w = csv.DictWriter(f, fieldnames=['IHE-MADO', 'EU-MADO', 'MS', 'Consumer', 'Producer', 'Documentation', 'EHDS', 'EHDS-Consumer', 'EHDS-Producer'])
            w.writeheader()
            w.writerows(step6_rows)

    print(f'WROTE {OUT_CSV_STEP6} rows={len(step6_rows)}')

    # ===== STEP 7: Parse mapping.csv to extract DICOM KOS Mappings =====
    # Step 7 outputs mapping.csv data only with its 4 columns: Concept, FHIR Imaging Study Manifest, Profile, DICOM KOS Manifest
    # A comma in FHIR Imaging Study Manifest is treated as a separator: each trimmed token becomes its own entry.
    # Column C (Profile) is populated with the IHE-MADO profile path from Column B.
    # If Column B contains "->", use only the part after the last "->".
    # Also build lookup dicts for Step 8 enrichment
    step7_rows = []
    mapping_fhir = {}  # IHE-MADO -> FHIR Imaging Study Manifest
    mapping_dicom = {}  # IHE-MADO -> DICOM KOS Manifest
    mapping_entries = []
    try:
        with open(MAPPING_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                concept = row.get('Concept', '').strip()
                fhir_raw = row.get('FHIR Imaging Study Manifest', '').strip()
                profile = row.get('Profile', '').strip()
                dicom_col = row.get('DICOM KOS Manifest', '').strip()
                
                if not fhir_raw or not dicom_col:
                    continue
                
                # Split on comma; each trimmed token is a distinct FHIR reference
                for token in fhir_raw.split(','):
                    fhir_col = token.strip()
                    if fhir_col:
                        # Extract IHE-MADO profile path: if "->" exists, use part after last "->", otherwise use fhir_col
                        if '->' in fhir_col:
                            ihe_mado_profile = fhir_col.split('->')[-1].strip()
                        else:
                            ihe_mado_profile = fhir_col
                        
                        # Store in lookups for Step 8: map IHE-MADO to FHIR and DICOM values
                        mapping_fhir[ihe_mado_profile] = fhir_col
                        mapping_dicom[ihe_mado_profile] = dicom_col
                        mapping_entries.append((fhir_col, ihe_mado_profile, dicom_col))
                        
                        # Add to Step 7 with only mapping.csv 4 columns
                        step7_rows.append(OrderedDict([
                            ('Concept', concept),
                            ('FHIR Imaging Study Manifest', fhir_col),
                            ('IHE-MADO', ihe_mado_profile),
                            ('DICOM KOS Manifest', dicom_col),
                        ]))
    except FileNotFoundError:
        print(f'Warning: Mapping file {MAPPING_CSV} not found. Step 7 will have empty data.', file=sys.stderr)
    except Exception as e:
        print(f'Warning: Failed to load mapping file {MAPPING_CSV}: {e}', file=sys.stderr)

    # Deduplicate Step 7 rows
    step7_rows = deduplicate_rows(step7_rows)
    with open(OUT_CSV_STEP7, 'w', newline='', encoding='utf-8') as f:
        if step7_rows:
            w = csv.DictWriter(f, fieldnames=['Concept', 'FHIR Imaging Study Manifest', 'IHE-MADO', 'DICOM KOS Manifest'])
            w.writeheader()
            w.writerows(step7_rows)

    print(f'WROTE {OUT_CSV_STEP7} rows={len(step7_rows)}')

    # ===== STEP 8: Enrich with XtEHR model mappings =====
    # This step enriches Step 7 mapping data and Step 6 EHDS-only rows with EU-MADO cross-references from XtEHR model mappings
    xtehr_mappings = load_xtehr_model_mappings()
    
    # Count actual mappings loaded
    actual_mapping_count = 0
    for xtehr_class in xtehr_mappings.values():
        for field_data in xtehr_class.values():
            if field_data.get('eu_resource') and field_data.get('eu_field') and field_data.get('eu_resource') not in ('N/A', '.'):
                actual_mapping_count += 1
    
    print(f'Loaded XtEHR model mappings: {len(xtehr_mappings)} classes, {actual_mapping_count} populated field mappings', file=sys.stderr)
    
    # Build a mapping dict of EHDS field -> EU-MADO for Step 6 enrichment
    # Key: (EHDS class).(EHDS field), Value: (EU resource).(EU field)
    xtehr_enrichments = {}
    for xtehr_class, fields_dict in xtehr_mappings.items():
        for xtehr_field, mapping_info in fields_dict.items():
            eu_resource = mapping_info.get('eu_resource', '').strip()
            eu_field = mapping_info.get('eu_field', '').strip()
            if eu_resource and eu_field and eu_resource not in ('N/A', '.') and eu_field not in ('N/A', '.'):
                ehds_key = f"{xtehr_class}.{xtehr_field}"
                eu_mado_value = f"{eu_resource}.{eu_field}"
                xtehr_enrichments[ehds_key] = eu_mado_value
    
    step8_rows = []
    step7_enrichment_count = 0
    step6_enrichment_count = 0
    
    # STEP 8A: Enrich Step 7 rows (DICOM KOS mappings)
    with open(OUT_CSV_STEP7, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            concept = row.get('Concept', '').strip()
            fhir_manifest = row.get('FHIR Imaging Study Manifest', '').strip()
            ihe_mado = row.get('IHE-MADO', '').strip()
            dicom_kos = row.get('DICOM KOS Manifest', '').strip()
            
            # Try to find matching XtEHR mappings
            enriched_eu_mado = None
            
            # Strategy: extract profile and field from IHE-MADO, normalize field, match against XtEHR
            # Example: "MadoImagingStudy.modality" -> ImagingStudy.modality -> EHDSImagingStudy.modality
            if ihe_mado and '.' in ihe_mado:
                ihe_parts = ihe_mado.split('.')
                ihe_profile = ihe_parts[0]
                ihe_field_part = '.'.join(ihe_parts[1:])
                
                # Normalize IHE field (remove slice notation for matching)
                ihe_field_base = ihe_field_part.split('[')[0] if '[' in ihe_field_part else ihe_field_part
                
                # Try to find corresponding EHDS class and field in xtehr mappings
                for xtehr_class in xtehr_mappings.keys():
                    ihe_prof_lower = ihe_profile.lower()
                    xtehr_lower = xtehr_class.lower()
                    
                    # Check if this could be a match
                    if ('imagingstudy' in ihe_prof_lower and 'imagingstudy' in xtehr_lower) or \
                       ('patient' in ihe_prof_lower and 'patient' in xtehr_lower):
                        if ihe_field_base in xtehr_mappings[xtehr_class]:
                            mapping_info = xtehr_mappings[xtehr_class][ihe_field_base]
                            eu_resource = mapping_info.get('eu_resource', '').strip()
                            eu_field = mapping_info.get('eu_field', '').strip()
                            
                            # Build EU-MADO cross-reference if both resource and field are populated
                            if eu_resource and eu_field and eu_resource not in ('N/A', '.') and eu_field not in ('N/A', '.'):
                                enriched_eu_mado = f"{eu_resource}.{eu_field}"
                                step7_enrichment_count += 1
            
            # Store enriched mapping with metadata about source
            row_out = OrderedDict([
                ('Concept', concept),
                ('FHIR Imaging Study Manifest', fhir_manifest),
                ('IHE-MADO', ihe_mado),
                ('DICOM KOS Manifest', dicom_kos),
                ('EU-MADO-from-XtEHR', enriched_eu_mado if enriched_eu_mado else ''),
                ('Enrichment-Note', 'Added from XtEHR mapping' if enriched_eu_mado else ''),
            ])
            
            step8_rows.append(row_out)
    
    # STEP 8B: Enrich Step 6 EHDS-only rows (those with empty EU-MADO and non-empty EHDS)
    step6_enriched_rows = []
    with open(OUT_CSV_STEP6, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ihe_mado_col = row.get('IHE-MADO', '').strip()
            eu_mado_col = row.get('EU-MADO', '').strip()
            ehds_col = row.get('EHDS', '').strip()
            
            # Check if this is an EHDS-only row (empty IHE-MADO and EU-MADO, but has EHDS)
            if not ihe_mado_col and not eu_mado_col and ehds_col and '.' in ehds_col:
                # Try to find enrichment in xtehr_enrichments
                if ehds_col in xtehr_enrichments:
                    eu_mado_enriched = xtehr_enrichments[ehds_col]
                    # Store for tracking (we'll update the row later in Step 9)
                    step6_enriched_rows.append({
                        'ehds_field': ehds_col,
                        'enriched_eu_mado': eu_mado_enriched,
                    })
                    step6_enrichment_count += 1
    
    step8_rows = deduplicate_rows(step8_rows)
    with open(OUT_CSV_STEP8, 'w', newline='', encoding='utf-8') as f:
        if step8_rows:
            w = csv.DictWriter(f, fieldnames=['Concept', 'FHIR Imaging Study Manifest', 'IHE-MADO', 'DICOM KOS Manifest', 'EU-MADO-from-XtEHR', 'Enrichment-Note'])
            w.writeheader()
            w.writerows(step8_rows)

    print(f'WROTE {OUT_CSV_STEP8} rows={len(step8_rows)} with {step7_enrichment_count} Step 7 enrichments from XtEHR mappings')
    print(f'Identified {step6_enrichment_count} Step 6 EHDS-only rows for EU-MADO enrichment', file=sys.stderr)

    # ===== STEP 9: Final merged inventory (Step 7 + XtEHR enrichment + Step 6 mapping data) =====
    # Merge Step 6 rows with DICOM KOS mappings, then add unmapped mapping entries
    final_rows = []
    step9_ihe_keys = set()

    # Build normalized key index only for mismatch diagnostics (strict matching is preserved).
    mapping_norm_to_keys = {}
    for key in mapping_fhir:
        norm = _normalize_ihe_key_for_match(key)
        mapping_norm_to_keys.setdefault(norm, []).append(key)

    # First, merge Step 6 rows with mapping lookups
    with open(OUT_CSV_STEP6, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ihe_mado = row.get('IHE-MADO', '').strip()
            # Look up the FHIR Imaging Study Manifest and DICOM KOS Manifest values from mapping
            fhir_imaging_manifest = ''
            dicom_kos = ''
            if ihe_mado and ihe_mado in mapping_fhir:
                fhir_imaging_manifest = mapping_fhir[ihe_mado]
                dicom_kos = mapping_dicom.get(ihe_mado, '')
                step9_ihe_keys.add(ihe_mado)
            elif ihe_mado:
                norm = _normalize_ihe_key_for_match(ihe_mado)
                for candidate in mapping_norm_to_keys.get(norm, []):
                    if _is_camel_vs_kebab_slice_mismatch(ihe_mado, candidate):
                        print(
                            f"WARNING Step9 slice-name mismatch (camelCase vs kebab-case): "
                            f"Step6 IHE-MADO '{ihe_mado}' vs mapping IHE-MADO '{candidate}'.",
                            file=sys.stderr,
                        )
                        break
            
            # Apply XtEHR enrichments to EU-MADO if empty
            eu_mado_value = row.get('EU-MADO', '').strip()
            ehds_value = row.get('EHDS', '').strip()
            if not eu_mado_value and ehds_value in xtehr_enrichments:
                eu_mado_value = xtehr_enrichments[ehds_value]
            
            final_rows.append(OrderedDict([
                ('IHE-MADO', row.get('IHE-MADO', '')),
                ('FHIR Imaging Study Manifest', fhir_imaging_manifest),
                ('EU-MADO', eu_mado_value),
                ('MS', row.get('MS', '')),
                ('Consumer', row.get('Consumer', '')),
                ('Producer', row.get('Producer', '')),
                ('Documentation', row.get('Documentation', '')),
                ('EHDS', row.get('EHDS', '')),
                ('EHDS-Consumer', row.get('EHDS-Consumer', '')),
                ('EHDS-Producer', row.get('EHDS-Producer', '')),
                ('DICOM-KOS', dicom_kos),
            ]))

    # Append mapping.csv rows that did not match any Step 6 IHE-MADO entry
    for fhir_col, ihe_mado_profile, dicom_col in mapping_entries:
        if ihe_mado_profile in step9_ihe_keys:
            continue
        final_rows.append(OrderedDict([
            ('IHE-MADO', ''),
            ('FHIR Imaging Study Manifest', fhir_col),
            ('EU-MADO', ''),  
            ('MS', ''),
            ('Consumer', ''),
            ('Producer', ''),
            ('Documentation', ''),
            ('EHDS', ''),
            ('EHDS-Consumer', ''),
            ('EHDS-Producer', ''),
            ('DICOM-KOS', dicom_col),
        ]))

    # Deduplicate Step 9 rows
    final_rows = deduplicate_rows(final_rows)
    with open(OUT_CSV_STEP9, 'w', newline='', encoding='utf-8') as f:
        if final_rows:
            w = csv.DictWriter(f, fieldnames=['IHE-MADO', 'FHIR Imaging Study Manifest', 'EU-MADO', 'MS', 'Consumer', 'Producer', 'Documentation', 'EHDS', 'EHDS-Consumer', 'EHDS-Producer', 'DICOM-KOS'])
            w.writeheader()
            w.writerows(final_rows)

    print(f'WROTE {OUT_CSV_STEP9} rows={len(final_rows)}')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
