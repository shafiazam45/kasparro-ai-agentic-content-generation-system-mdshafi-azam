# agents/run_mock_orchestrator.py
"""
Robust mock orchestrator — loads agent modules by file path and registers them
under package-style names in sys.modules so internal 'from agents.xxx import ...'
works. This avoids package/importpath issues.

Run:
    python .\agents\run_mock_orchestrator.py
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root
AGENTS_DIR = ROOT / "agents"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_register(name: str, path: Path, package_prefix: str = "agents"):
    """
    Load module from path and register in sys.modules under two keys:
      - simple name (e.g., 'parsing_agent')
      - package name (e.g., 'agents.parsing_agent')
    Returns the module object.
    """
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {path}")

    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None:
        raise ImportError(f"Cannot load spec for {name} at {path}")
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError(f"No loader for spec {spec} (module {name})")
    # execute module
    loader.exec_module(mod)

    # register in sys.modules under both names so intra-package imports work
    sys.modules[name] = mod
    pkg_name = f"{package_prefix}.{name}"
    sys.modules[pkg_name] = mod
    return mod


# Expected files
expected_files = [
    "parsing_agent.py",
    "question_agent.py",
    "logic_block_agent.py",
    "template_engine_agent.py",
    "page_assembly_agent.py",
]

missing = [f for f in expected_files if not (AGENTS_DIR / f).exists()]
if missing:
    raise FileNotFoundError(f"Missing agent files in agents/: {missing}. Please ensure these files exist.")

# Load & register modules under 'agents.<module>'
parsing_mod = load_and_register("parsing_agent", AGENTS_DIR / "parsing_agent.py")
question_mod = load_and_register("question_agent", AGENTS_DIR / "question_agent.py")
logic_mod = load_and_register("logic_block_agent", AGENTS_DIR / "logic_block_agent.py")
template_mod = load_and_register("template_engine_agent", AGENTS_DIR / "template_engine_agent.py")
page_assembly_mod = load_and_register("page_assembly_agent", AGENTS_DIR / "page_assembly_agent.py")

# Now imports like "from agents.template_engine_agent import ..." will resolve.

# Alias functions we need
parse_raw_dataset = parsing_mod.parse_raw_dataset
generate_questions = question_mod.generate_questions

build_faq_page = page_assembly_mod.build_faq_page
build_product_page = page_assembly_mod.build_product_page
build_comparison_page = page_assembly_mod.build_comparison_page
write_json = page_assembly_mod.write_json

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


def make_product_b():
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
    print("Mock orchestrator (registered-loader) starting...")

    # parse
    product = parse_raw_dataset(RAW_PRODUCT)
    print("Parsed product:", product["name"])

    # questions
    questions = generate_questions(product, min_questions=15)
    print("Generated", len(questions), "questions")

    # build pages
    faq_page = build_faq_page(product, questions)
    product_page = build_product_page(product)
    product_b = make_product_b()
    comparison_page = build_comparison_page(product, product_b)

    # write outputs
    write_json("faq.json", faq_page)
    write_json("product_page.json", product_page)
    write_json("comparison_page.json", comparison_page)

    print("Done. Files written to ./output/")


if __name__ == "__main__":
    main()


