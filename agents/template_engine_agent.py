"""
template_engine_agent.py (fixed)
Responsibility:
- Load JSON templates from /templates and render them using content blocks.
- Robust templating engine: detects if a placeholder is inside string quotes and
  adapts replacement so final string is valid JSON before parsing.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}")


def load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def _lookup_context(context: Dict[str, Any], key: str):
    """Look up nested key using dot notation. Return None if missing."""
    parts = key.split(".")
    cur = context
    for p in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
        if cur is None:
            return None
    return cur


def render_template(template_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replaces placeholders in template_text using context dictionary.

    Behavior:
    - If the placeholder is inside JSON string quotes (like: "field": "{{some.key}}"),
      and the replacement is a primitive (str/int/float/bool/None), we inject the
      primitive value properly escaped *without adding an extra pair of quotes*.
      This prevents double-quoting like: "\"value\"" which can break JSON parsing.
    - If replacement is list/dict, we inject its JSON literal (so templates should
      leave the placeholder unquoted when expecting arrays/objects).
    """

    filled_parts = []
    last_index = 0

    for match in PLACEHOLDER_PATTERN.finditer(template_text):
        start, end = match.span()
        key = match.group(1)

        filled_parts.append(template_text[last_index:start])

        before = template_text[:start]
        after = template_text[end:]
        char_before = before[-1] if before else ""
        char_after = after[0] if after else ""

        inside_quotes = (char_before == '"' and char_after == '"')

        value = _lookup_context(context, key)

        if value is None:
            replacement_text = "null"
            if inside_quotes:
                replacement_text = ""
            filled_parts.append(replacement_text)
            last_index = end
            continue

        if isinstance(value, (dict, list)):
            replacement_text = json.dumps(value, ensure_ascii=False)
            filled_parts.append(replacement_text)
            last_index = end
            continue

        if inside_quotes:
            json_prim = json.dumps(value, ensure_ascii=False)
            if len(json_prim) >= 2 and json_prim[0] == '"' and json_prim[-1] == '"':
                inner = json_prim[1:-1]
            else:
                inner = json_prim
            filled_parts.append(inner)
        else:
            replacement_text = json.dumps(value, ensure_ascii=False)
            filled_parts.append(replacement_text)

        last_index = end

    filled_parts.append(template_text[last_index:])
    filled = "".join(filled_parts)

    return json.loads(filled)

