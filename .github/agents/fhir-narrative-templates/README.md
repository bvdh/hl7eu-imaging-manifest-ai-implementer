# FHIR Narrative Templates

This directory contains user-editable Liquid/Jekyll-style XHTML templates used by the **FHIR Narrative Generator** agent.

Each template starts with YAML frontmatter. Resource templates are keyed by `resourceType`; Composition section templates are keyed by the full `system` and `code` pair. The wildcard section template applies only to sections without a code.

Supported conventions:

- `{{ value }}` outputs a value from the FSH instance.
- `{% if value %}...{% endif %}` includes optional content.
- `{% for item in items %}...{% endfor %}` renders repeating content.
- Dotted paths access nested values, for example `subject.display`.

The template body must produce one valid FHIR Narrative XHTML `div` with `xmlns="http://www.w3.org/1999/xhtml"`.

Use two-space indentation and place XHTML elements and Liquid control tags on separate lines. Fixed XHTML remains literal; dynamic values and blocks are marked by `{{ ... }}` and `{% ... %}`. The agent preserves line breaks in a quoted FSH string as literal `\n` escapes, including the indentation after each escape.
