"""
page_assembly_agent.py
Assembles pages using templates and logic blocks; writes JSON outputs.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from agents.template_engine_agent import load_template, render_template
from agents.logic_block_agent import (
    summary_block,
    benefit_block,
    usage_block,
    safety_block,
    compare_ingredients_block,
    compare_benefits_block,
    price_diff_block,
    faq_answer_block,
)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def build_faq_page(product: Dict[str, Any], questions: List[Dict[str, str]]) -> Dict[str, Any]:
    template_text = load_template("faq_template.json")
    selected = questions[: max(5, len(questions))]
    faqs = []
    for q in selected:
        ans = faq_answer_block(q["question"], product)
        faqs.append({"question": q["question"], "answer": ans, "category": q.get("category")})
    page_json = render_template(template_text, {"product": product, "faqs": faqs})
    return page_json


def build_product_page(product: Dict[str, Any]) -> Dict[str, Any]:
    template_text = load_template("product_template.json")
    context = {
        "product": {
            "name": product["name"],
            "summary": summary_block(product),
            "key_ingredients": product.get("ingredients", []),
            "benefits": benefit_block(product),
            "how_to_use": usage_block(product),
            "safety_info": safety_block(product),
            "price": product.get("price"),
            "concentration": product.get("concentration"),
            "skin_type": product.get("skin_type"),
        }
    }
    page_json = render_template(template_text, context)
    return page_json


def build_comparison_page(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Dict[str, Any]:
    template_text = load_template("comparison_template.json")
    context = {
        "productA": {"name": prod_a["name"], "price": prod_a["price"], "ingredients": prod_a["ingredients"], "benefits": prod_a["benefits"]},
        "productB": {"name": prod_b["name"], "price": prod_b["price"], "ingredients": prod_b["ingredients"], "benefits": prod_b["benefits"]},
        "comparison": {
            "price_diff": price_diff_block(prod_a, prod_b),
            "ingredient_comparison": compare_ingredients_block(prod_a, prod_b),
            "benefit_comparison": compare_benefits_block(prod_a, prod_b),
        },
    }
    page_json = render_template(template_text, context)
    return page_json


def write_json(filename: str, data: Dict[str, Any]):
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {path}")
