"""
logic_block_agent.py
Responsibility:
- Provide reusable content logic blocks (pure functions)
- Each function uses only the internal product model
"""

from typing import Dict, List, Any


def summary_block(product: Dict[str, Any], max_sentences: int = 2) -> str:
    name = product["name"]
    conc = product.get("concentration", "")
    benefits = product.get("benefits", [])
    skin_types = product.get("skin_type", [])
    s1 = f"{name} is a serum containing {conc}."
    s2 = f"It is formulated for {', '.join(skin_types)} skin and aims to {', '.join(benefits)}."
    return " ".join([s1, s2]) if max_sentences >= 2 else s1


def benefit_block(product: Dict[str, Any]) -> List[str]:
    return product.get("benefits", [])


def usage_block(product: Dict[str, Any]) -> str:
    return product.get("how_to_use", "")


def safety_block(product: Dict[str, Any]) -> str:
    se = product.get("side_effects", "")
    if not se:
        return "No side effects recorded."
    return f"{se} If irritation occurs, discontinue use and consult a dermatologist."


def compare_ingredients_block(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Dict[str, List[str]]:
    a_ing = set([i.lower() for i in prod_a.get("ingredients", [])])
    b_ing = set([i.lower() for i in prod_b.get("ingredients", [])])
    common = sorted([i.title() for i in (a_ing & b_ing)])
    only_a = sorted([i.title() for i in (a_ing - b_ing)])
    only_b = sorted([i.title() for i in (b_ing - a_ing)])
    return {"common": common, "a_only": only_a, "b_only": only_b}


def compare_benefits_block(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Dict[str, List[str]]:
    a_ben = set([b.lower() for b in prod_a.get("benefits", [])])
    b_ben = set([b.lower() for b in prod_b.get("benefits", [])])
    return {
        "a_only": sorted([b.title() for b in (a_ben - b_ben)]),
        "b_only": sorted([b.title() for b in (b_ben - a_ben)]),
        "common": sorted([b.title() for b in (a_ben & b_ben)]),
    }


def price_diff_block(prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> str:
    pa = prod_a.get("price", 0)
    pb = prod_b.get("price", 0)
    if pa == pb:
        return "Both products are priced the same."
    elif pa < pb:
        return f"{prod_b['name']} is ₹{pb - pa} more expensive than {prod_a['name']}."
    else:
        return f"{prod_a['name']} is ₹{pa - pb} more expensive than {prod_b['name']}."


def faq_answer_block(question: str, product: Dict[str, Any]) -> str:
    """
    Conservative rule-based answers derived purely from product fields.
    Avoid inventing any external facts.
    """
    q = question.lower()
    name = product["name"]
    if "what does" in q or "what is" in q:
        benefits = product.get("benefits", [])
        conc = product.get("concentration", "")
        return f"{name} provides {', '.join(benefits)} and contains {conc}."
    if "suitable" in q or "who is" in q:
        return f"It is suitable for {', '.join(product.get('skin_type', []))} skin types."
    if "how should i use" in q or "how many" in q or "when is the best time" in q:
        return product.get("how_to_use", "")
    if "side effect" in q or "irritation" in q:
        return product.get("side_effects", "")
    if "price" in q or "cost" in q:
        return f"₹{product.get('price')}"
    if "ingredients" in q:
        return ", ".join(product.get("ingredients", []))
    # fallback safe answer
    return f"For {question}, refer to the product information provided: {product.get('name')}."
