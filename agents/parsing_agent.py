"""
parsing_agent.py
Responsibility:
- Validate & normalize the provided product dataset into a strict internal model.
No external calls. Stateless.
"""

from typing import Dict, Any, List


REQUIRED_FIELDS = [
    "Product Name",
    "Concentration",
    "Skin Type",
    "Key Ingredients",
    "Benefits",
    "How to Use",
    "Side Effects",
    "Price",
]


def parse_raw_dataset(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: raw JSON-like dict (as provided in the assignment)
    Output: normalized internal model
    """
    missing = [f for f in REQUIRED_FIELDS if f not in raw]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    name = raw["Product Name"].strip()
    price_raw = raw["Price"]
    price = _parse_price(price_raw)

    concentration = raw["Concentration"].strip()
    skin_type = _ensure_list(raw["Skin Type"])
    ingredients = _ensure_list(raw["Key Ingredients"])
    benefits = _ensure_list(raw["Benefits"])
    how_to_use = raw["How to Use"].strip()
    side_effects = raw["Side Effects"].strip()

    model = {
        "name": name,
        "concentration": concentration,
        "skin_type": skin_type,
        "ingredients": ingredients,
        "benefits": benefits,
        "how_to_use": how_to_use,
        "side_effects": side_effects,
        "price": price,
    }
    return model


def _ensure_list(value) -> List[str]:
    if isinstance(value, str):
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]
    elif isinstance(value, list):
        return [str(x).strip() for x in value]
    else:
        return [str(value).strip()]


def _parse_price(value) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        v = value.strip().replace("₹", "").replace("INR", "").replace(",", "").strip()
        try:
            return int(float(v))
        except Exception:
            raise ValueError(f"Unable to parse price: {value}")
    raise ValueError(f"Unsupported price type: {type(value)}")
