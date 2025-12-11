# agents/template_engine_agent.py
"""
Robust template engine for JSON templates.

- Handles placeholders like {{key}} or {{product.name}}.
- Detects whether the placeholder appears inside JSON string quotes and
  injects appropriately to avoid double-quoting.
- Embeds lists/dicts as JSON literals.
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
    """Lookup nested key via dot notation; return None if missing."""
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
    Replace placeholders in template_text using context dict.

    Behavior:
    - If placeholder is inside quotes in the template and the replacement is a primitive string,
      the function injects the escaped inner string content (without additional outer quotes).
    - If placeholder is unquoted and replacement is primitive, inject JSON literal (with quotes for strings).
    - If replacement is list/dict, inject JSON literal (templates must leave such placeholders unquoted).
    """

    filled_parts = []
    last_index = 0

    for match in PLACEHOLDER_PATTERN.finditer(template_text):
        start, end = match.span()
        key = match.group(1)

        # append text before match
        filled_parts.append(template_text[last_index:start])

        # detect surrounding characters to check if placeholder is inside JSON quotes
        before = template_text[:start]
        after = template_text[end:]
        char_before = before[-1] if before else ""
        char_after = after[0] if after else ""
        inside_quotes = (char_before == '"' and char_after == '"')

        # lookup value
        value = _lookup_context(context, key)

        # If value missing -> insert null (respect quotes: if inside quotes leave empty string)
        if value is None:
            if inside_quotes:
                filled_parts.append("")  # keep template quotes, insert empty string
            else:
                filled_parts.append("null")
            last_index = end
            continue

        # If value is list/dict -> insert JSON literal (templates should have unquoted placeholder)
        if isinstance(value, (list, dict)):
            filled_parts.append(json.dumps(value, ensure_ascii=False))
            last_index = end
            continue

        # For primitives (str/int/float/bool)
        # If placeholder is inside quotes -> produce JSON string and strip outer quotes
        if inside_quotes:
            json_prim = json.dumps(value, ensure_ascii=False)
            # If json_prim is a quoted string, strip the outer quotes to avoid double quotes
            if isinstance(json_prim, str) and len(json_prim) >= 2 and json_prim[0] == '"' and json_prim[-1] == '"':
                inner = json_prim[1:-1]
            else:
                inner = json_prim
            filled_parts.append(inner)
        else:
            # not inside quotes -> inject JSON literal (strings will be quoted)
            filled_parts.append(json.dumps(value, ensure_ascii=False))

        last_index = end

    # append remainder
    filled_parts.append(template_text[last_index:])
    filled = "".join(filled_parts)

    # parse into JSON and return
    return json.loads(filled)

