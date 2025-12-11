"""
Utility helpers.
"""

import json
from pathlib import Path
from typing import Dict, Any


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def write_json(filename: str, data: Dict[str, Any]):
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {path}")


def load_assignment_product() -> Dict[str, Any]:
    """
    Return the exact assignment input dataset (the ONLY allowed input).
    Keep this in code for reproducibility.
    """
    return {
        "Product Name": "GlowBoost Vitamin C Serum",
        "Concentration": "10% Vitamin C",
        "Skin Type": "Oily, Combination",
        "Key Ingredients": "Vitamin C, Hyaluronic Acid",
        "Benefits": "Brightening, Fades dark spots",
        "How to Use": "Apply 2–3 drops in the morning before sunscreen",
        "Side Effects": "Mild tingling for sensitive skin",
        "Price": "₹699",
    }


def safe_parse_price(price_str: str) -> int:
    # simple sanitizer: remove currency symbol and parse int
    v = str(price_str).strip().replace("₹", "").replace("INR", "").replace(",", "").strip()
    return int(float(v))
