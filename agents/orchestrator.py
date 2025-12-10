"""
orchestrator.py
Responsibility:
- Drive the pipeline: parse -> generate questions -> create blocks -> assemble pages -> write outputs
"""

import json
from pathlib import Path

from agents.parsing_agent import parse_raw_dataset
from agents.question_agent import generate_questions
from agents.page_assembly_agent import build_faq_page, build_product_page, build_comparison_page, write_json

RAW_PRODUCT = {
    "Product Name": "GlowBoost Vitamin C Serum",
    "Concentration": "10% Vitamin C",
    "Skin Type": "Oily, Combination",
    "Key Ingredients": "Vitamin C, Hyaluronic Acid",
    "Benefits": "Brightening, Fades dark spots",
    "How to Use": "Apply 2–3 drops in the morning before sunscreen",
    "Side Effects": "Mild tingling for sensitive skin",
    "Price": "₹699",
}


def make_fictional_product_b() -> dict:
    # Product B must be fictional but structured
    return {
        "name": "DermaRadiance Serum",
        "concentration": "12% Vitamin C",
        "skin_type": ["Oily"],
        "ingredients": ["Vitamin C", "Niacinamide"],
        "benefits": ["Brightening", "Oil balancing"],
        "how_to_use": "Apply 2–3 drops in the morning; follow with moisturizer.",
        "side_effects": "May cause mild tingling for sensitive skin.",
        "price": 799,
    }


def main():
    print("Orchestrator: starting pipeline...")

    # 1. Parse
    product = parse_raw_dataset(RAW_PRODUCT)
    print("Parsed product:", product["name"])

    # 2. Question generation
    questions = generate_questions(product, min_questions=15)
    print(f"Generated {len(questions)} questions")

    # 3 & 4. Build pages
    faq_page = build_faq_page(product, questions)
    product_page = build_product_page(product)
    product_b = make_fictional_product_b()
    comparison_page = build_comparison_page(product, product_b)

    # 5. Write outputs
    write_json("faq.json", faq_page)
    write_json("product_page.json", product_page)
    write_json("comparison_page.json", comparison_page)

    print("Pipeline finished. Files in ./output/")


if __name__ == "__main__":
    main()
