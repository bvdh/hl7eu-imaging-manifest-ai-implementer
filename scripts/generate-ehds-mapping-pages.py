#!/usr/bin/env python3
"""
Generate EHDS mapping pages from authoritative Xt-EHR model mappings and EHDS logical models.

This script implements the generate-ehds-mapping-pages SKILL.md specification:
- Reads authoritative Xt-EHR to FHIR mappings from xtehr-model-mapping.csv
- Loads authoritative EHDS logical model StructureDefinitions
- Merges logical-model row inventory with xtehr-model-mapping.csv mappings
- Generates per-profile HTML table markdown files
"""

import csv
import json
import os
import re
import sys

# Constants
XTEHR_MAPPING_CSV = 'imaging-manifest-fork/input/mapping/xtehr-model-mapping.csv'
OUTPUT_DIR = 'imaging-manifest-fork/input/pagecontent'
XTEHR_MAPPING_PAGE = 'imaging-manifest-fork/input/pagecontent/xtehr-mapping.md'
EHDS_PACKAGE_PATH = os.path.expanduser('~/.fhir/packages/xtehr.eu.ehds.models#1.0.0/package')


def first_populated_value(row, *column_names):
    """Return the first non-empty value among the given CSV column names."""
    for column_name in column_names:
        value = row.get(column_name, '')
        if value is None:
            continue
        value = value.strip()
        if value:
            return value
    return ''


def load_logical_model(profile_name):
    """Load EHDS logical model StructureDefinition from FHIR package."""
    sd_path = os.path.join(EHDS_PACKAGE_PATH, f'StructureDefinition-{profile_name}.json')
    if not os.path.exists(sd_path):
        print(f'ERROR: StructureDefinition not found: {sd_path}', file=sys.stderr)
        return None
    
    with open(sd_path, 'r') as f:
        return json.load(f)


def extract_logical_model_elements(sd):
    """Extract all elements from logical model snapshot in order."""
    snapshot = sd.get('snapshot', {})
    elements = snapshot.get('element', [])
    
    # Convert to list of (path, definition) for easier processing
    result = []
    for elem in elements:
        path = elem.get('path', '')
        if not path:
            continue
        
        # Skip the root element (e.g., "EHDSImagingStudy" without dot)
        if '.' not in path:
            continue
        
        result.append({
            'path': path,
            'element': elem,
        })
    
    return result


def read_xtehr_mappings():
    """Read xtehr-model-mapping.csv and organize by EHDS profile and field.
    
    Returns two dicts:
    - mappings: profile -> field_name -> list of mapping dicts (only rows with target mappings)
    - field_rationale: profile -> field_name -> rationale string (all rows with rationale, regardless of target mapping)
    """
    mappings = {}  # profile -> field_name -> list of mapping dicts (only with target)
    field_rationale = {}  # profile -> field_name -> rationale (all rows with rationale)
    
    with open(XTEHR_MAPPING_CSV, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse row columns
            xtehr_class = row.get('XtEHR Class', '').strip()
            xtehr_field = row.get('XtEHR field', '').strip()
            eumado_resource = row.get('EuMado resource', '').strip()
            eumado_field = row.get('EuMado field', '').strip()
            rationale = row.get('Rationale', '').strip()
            detailed_desc = row.get('XtEHR detailed description', '').strip()
            kos = first_populated_value(
                row,
                'DICOM-KOS',
                'KOS (first occurance)',
                'KOS (first occurrence)',
            )
            
            # Skip rows without class or field
            if not xtehr_class or not xtehr_field:
                continue
            
            # Use Rationale column, or fall back to detailed description if empty
            effective_rationale = rationale if rationale else detailed_desc
            
            # Store rationale for all rows (even those without target mappings)
            if effective_rationale:
                if xtehr_class not in field_rationale:
                    field_rationale[xtehr_class] = {}
                field_rationale[xtehr_class][xtehr_field] = effective_rationale
            
            # Only store target mapping if both resource and field are present
            if not eumado_resource or not eumado_field:
                continue
            
            # Organize by profile and field
            if xtehr_class not in mappings:
                mappings[xtehr_class] = {}
            
            if xtehr_field not in mappings[xtehr_class]:
                mappings[xtehr_class][xtehr_field] = []
            
            # Add the mapping with all metadata
            mappings[xtehr_class][xtehr_field].append({
                'target_resource': eumado_resource,
                'target_element': eumado_field,
                'rationale': rationale,
                'kos': kos,
            })
    
    return mappings, field_rationale


def get_target_mapping(mapping_dict):
    """Extract target resource, element, rationale, and KOS from xtehr mapping dict."""
    return (mapping_dict.get('target_resource', ''),
            mapping_dict.get('target_element', ''),
            mapping_dict.get('rationale', ''),
            mapping_dict.get('kos', ''))


def discover_profiles_with_mappings(mappings):
    """Discover which EHDS profiles have at least one mapping in xtehr-model-mapping.csv."""
    # Return sorted list of profile names that have mappings
    return sorted(mappings.keys())


def discover_profiles_from_mapping_page():
    """Discover EHDS profiles referenced by include statements in xtehr-mapping.md."""
    include_profiles = []
    if not os.path.exists(XTEHR_MAPPING_PAGE):
        return include_profiles

    include_pattern = re.compile(r'\{\%\s*include\s+([A-Za-z0-9_-]+)-mapping\.md\s*\%\}')
    with open(XTEHR_MAPPING_PAGE, 'r', encoding='utf-8') as f:
        for line in f:
            match = include_pattern.search(line)
            if match:
                include_profiles.append(match.group(1))

    # Preserve include order while removing duplicates
    seen = set()
    ordered_unique = []
    for profile in include_profiles:
        if profile not in seen:
            seen.add(profile)
            ordered_unique.append(profile)
    return ordered_unique


def normalize_profile_arg(profile):
    """Normalize optional CLI profile arg to a profile name without suffix."""
    normalized = profile.strip()
    if normalized.endswith('-mapping.md'):
        normalized = normalized[:-11]
    elif normalized.endswith('-mapping'):
        normalized = normalized[:-8]
    return normalized


def discover_profiles_to_generate(mappings, requested_profiles=None):
    """Build final profile list from mappings, include page, and optional explicit profile args."""
    mapped_profiles = discover_profiles_with_mappings(mappings)
    include_profiles = discover_profiles_from_mapping_page()

    combined = []
    seen = set()
    for profile in include_profiles + mapped_profiles:
        if profile not in seen:
            seen.add(profile)
            combined.append(profile)

    if requested_profiles:
        requested_set = set(requested_profiles)
        combined = [profile for profile in combined if profile in requested_set]

    return combined, mapped_profiles, include_profiles


def generate_table_rows(profile_name, logical_model_elements, mappings, field_rationale):
    """
    Generate final table rows by merging logical model with xtehr-model-mapping.csv mappings.
    
    Returns list of dicts with keys: ehds_element, target_resource, target_element, rationale, kos
    
    All logical model elements are included, with or without mappings.
    When an element has no target mapping, use rationale from field_rationale if available.
    """
    rows = []
    
    profile_mappings = mappings.get(profile_name, {})
    profile_rationale = field_rationale.get(profile_name, {})
    
    for lm_elem in logical_model_elements:
        element_path = lm_elem['path'].split('.', 1)[1]  # Remove profile prefix
        element_def = lm_elem['element']
        
        # Check if this element has mappings in xtehr-model-mapping.csv
        element_mappings = profile_mappings.get(element_path, [])
        
        # Collect all valid mappings for this element
        if element_mappings:
            for mapping in element_mappings:
                target_resource, target_element, rationale, kos = get_target_mapping(mapping)
                
                rows.append({
                    'ehds_element': element_path,
                    'target_resource': target_resource,
                    'target_element': target_element,
                    'rationale': rationale,
                    'kos': kos,
                })
        else:
            # If no mapping found for this element, still emit it as unmapped
            # but use rationale from CSV if available
            csv_rationale = profile_rationale.get(element_path, '')
            rows.append({
                'ehds_element': element_path,
                'target_resource': '',
                'target_element': '',
                'rationale': csv_rationale,
                'kos': '',
            })
    
    # Deduplicate by full cell tuple
    seen = set()
    deduped = []
    for row in rows:
        key = (row['ehds_element'], row['target_resource'], row['target_element'], row['kos'], row['rationale'])
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    
    return deduped


def render_table_rows_html(rows):
    """Render table rows as HTML tbody rows."""
    html = []
    for row in rows:
        html.append('  <tr>')
        
        # Element
        html.append(f"    <td>{escape_html(row['ehds_element'])}</td>")
        
        # Resource (create link if populated)
        if row['target_resource']:
            resource_html = f"<a href=\"./StructureDefinition-{escape_html(row['target_resource'])}.html\">{escape_html(row['target_resource'])}</a>"
            html.append(f"    <td>{resource_html}</td>")
        else:
            html.append("    <td></td>")
        
        # Element
        html.append(f"    <td>{escape_html(row['target_element'])}</td>")
        
        # DICOM KOS
        html.append(f"    <td>{escape_html(row['kos'])}</td>")

        # Rationale
        html.append(f"    <td>{escape_html(row['rationale'])}</td>")
        
        html.append('  </tr>')
    
    return '\n'.join(html)


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def generate_markdown_file(profile_name, rows):
    """Generate markdown content for a profile's mapping page."""
    lines = []
    
    # Heading
    lines.append(f"#### {profile_name}")
    lines.append('')
    
    # Intro sentence
    lines.append(f'The following table shows the mapping from {profile_name} logical model elements to FHIR profiles.')
    lines.append('')
    
    # Mapping context block
    lines.append('<div class="table-wrap">')
    lines.append('  <strong>Mapping Context</strong>')
    lines.append('  <ul>')
    lines.append('    <li>')
    lines.append('      <strong>Source logical model:</strong>')
    lines.append(f'      <a href="https://www.xt-ehr.eu/fhir/models/1.0.0/StructureDefinition-{profile_name}.html" target="_blank">{profile_name}</a>')
    lines.append('    </li>')
    lines.append('  </ul>')
    lines.append('</div>')
    lines.append('')
    
    # Table wrapper and HTML table
    lines.append('<div class="table-wrap">')
    lines.append(f'  <table summary="{profile_name} → FHIR Profiles (R4)">')
    lines.append(f'    <caption>{profile_name} → FHIR Profiles (R4)</caption>')
    lines.append('    <thead>')
    lines.append('      <tr>')
    lines.append(f'        <th colspan="1" class="src-head">{profile_name} (Logical Model)</th>')
    lines.append('        <th colspan="2" class="tgt-fhir-head">Target FHIR Resource</th>')
    lines.append('        <th colspan="1" class="tgt-dicom-head">Target DICOM elements</th>')
    lines.append('        <th colspan="1" class="tgt-rationale-head">Rationale</th>')
    lines.append('      </tr>')
    lines.append('      <tr>')
    lines.append('        <th class="src-sub">Element</th>')
    lines.append('        <th class="tgt-fhir-sub">Resource</th>')
    lines.append('        <th class="tgt-fhir-sub">Element</th>')
    lines.append('        <th class="tgt-dicom-sub">DICOM KOS</th>')
    lines.append('        <th class="tgt-rationale-sub">Rationale</th>')
    lines.append('      </tr>')
    lines.append('    </thead>')
    lines.append('    <tbody>')
    
    # Render rows
    tbody_html = render_table_rows_html(rows)
    lines.append(tbody_html)
    
    lines.append('    </tbody>')
    lines.append('  </table>')
    lines.append('</div>')
    lines.append('<!--')
    lines.append('Generated file. Do not edit.')
    lines.append('-->')
    lines.append('')
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    print('=== Generate EHDS Mapping Pages ===', file=sys.stderr)
    
    # Check prerequisites
    if not os.path.exists(XTEHR_MAPPING_CSV):
        print(f'ERROR: {XTEHR_MAPPING_CSV} not found', file=sys.stderr)
        return 1
    
    if not os.path.exists(EHDS_PACKAGE_PATH):
        print(f'ERROR: EHDS package not found at {EHDS_PACKAGE_PATH}', file=sys.stderr)
        return 1
    
    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Read xtehr model mappings
    mappings, field_rationale = read_xtehr_mappings()

    requested_profiles = [normalize_profile_arg(arg) for arg in sys.argv[1:] if arg.strip()]
    if requested_profiles:
        print(f'Requested profiles: {", ".join(requested_profiles)}', file=sys.stderr)
    
    # Discover profiles from mappings and include page
    profiles_to_generate, mapped_profiles, include_profiles = discover_profiles_to_generate(
        mappings,
        requested_profiles=requested_profiles or None,
    )
    print(f'Profiles with mappings: {", ".join(mapped_profiles) if mapped_profiles else "(none)"}', file=sys.stderr)
    print(f'Profiles from xtehr-mapping includes: {", ".join(include_profiles) if include_profiles else "(none)"}', file=sys.stderr)
    print(f'Profiles to generate: {", ".join(profiles_to_generate) if profiles_to_generate else "(none)"}', file=sys.stderr)
    
    # Generate a file for each profile
    generated_count = 0
    for profile_name in profiles_to_generate:
        print(f'Generating {profile_name}-mapping.md...', file=sys.stderr)
        
        # Load logical model
        sd = load_logical_model(profile_name)
        if not sd:
            print(f'WARNING: Could not load logical model for {profile_name}', file=sys.stderr)
            continue
        
        # Extract logical model elements
        lm_elements = extract_logical_model_elements(sd)
        print(f'  Logical model has {len(lm_elements)} elements', file=sys.stderr)
        
        # Generate table rows
        table_rows = generate_table_rows(profile_name, lm_elements, mappings, field_rationale)
        print(f'  Generated {len(table_rows)} table rows', file=sys.stderr)
        
        # Generate markdown
        markdown = generate_markdown_file(profile_name, table_rows)
        
        # Write file
        output_file = os.path.join(OUTPUT_DIR, f'{profile_name}-mapping.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f'  WROTE {output_file}', file=sys.stderr)
        generated_count += 1
    
    print(f'Generated {generated_count} mapping files', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
