"""
question_agent.py
Responsibility:
- Produce at least 15 categorized user questions from the product model.
Stateless.
"""

from typing import Dict, List


DEFAULT_CATEGORIES = [
    "Informational",
    "Usage",
    "Safety",
    "Purchase",
    "Comparison",
    "Ingredients",
]


def generate_questions(product: Dict[str, any], min_questions: int = 15) -> List[Dict[str, str]]:
    name = product["name"]
    concentration = product.get("concentration", "")
    skin_types = product.get("skin_type", [])
    ingredients = product.get("ingredients", [])
    benefits = product.get("benefits", [])
    price = product.get("price")

    questions = []

    # Informational (4)
    questions += [
        {"question": f"What does {name} do?", "category": "Informational"},
        {"question": f"What is the active concentration in {name}?", "category": "Informational"},
        {"question": f"Who is {name} suitable for?", "category": "Informational"},
        {"question": f"What are the key ingredients in {name}?", "category": "Ingredients"},
    ]

    # Usage (3)
    questions += [
        {"question": f"How should I use {name}?", "category": "Usage"},
        {"question": f"How many drops of {name} should I apply?", "category": "Usage"},
        {"question": f"When is the best time to apply {name}?", "category": "Usage"},
    ]

    # Safety (3)
    questions += [
        {"question": f"Are there any side effects of {name}?", "category": "Safety"},
        {"question": f"Can sensitive skin use {name}?", "category": "Safety"},
        {"question": f"What should I do if I experience irritation from {name}?", "category": "Safety"},
    ]

    # Purchase (2)
    questions += [
        {"question": f"How much does {name} cost?", "category": "Purchase"},
        {"question": f"Where can I buy {name}?", "category": "Purchase"},
    ]

    # Comparison (3)
    questions += [
        {"question": f"How does {name} compare to Product B for brightening?", "category": "Comparison"},
        {"question": f"Is {name} better than Product B for oily skin?", "category": "Comparison"},
        {"question": f"What ingredients does {name} share with Product B?", "category": "Comparison"},
    ]

    # Add extra questions from benefits if needed
    if len(questions) < min_questions:
        for b in benefits:
            questions.append({"question": f"How does {name} help with {b.lower()}?", "category": "Informational"})
            if len(questions) >= min_questions:
                break

    # Deduplicate
    seen = set()
    unique = []
    for q in questions:
        key = (q["question"].strip().lower(), q["category"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)

    return unique[: max(min_questions, len(unique))]
