"""
langchain_orchestrator.py (robust imports)

This version uses defensive imports so it works across LangChain releases.
It uses ChatOpenAI from langchain_openai and LangChain chains (LLMChain + PromptTemplate)
with multiple import fallbacks.

Run:
  $env:OPENAI_API_KEY="sk-..."
  python -m agents.langchain_orchestrator
"""

import json
import os
from pathlib import Path

# Defensive imports for LLMChain and PromptTemplate (different langchain versions expose them in different modules)
try:
    # preferred for newer versions
    from langchain.chains import LLMChain
except Exception:
    try:
        from langchain.llms import LLMChain  # older layout (unlikely)
    except Exception:
        # final fallback - try the direct submodule that sometimes exists
        try:
            from langchain.chains.llm import LLMChain
        except Exception as e:
            raise ImportError("Could not import LLMChain from langchain. Try upgrading/downgrading langchain package.") from e

try:
    from langchain.prompts import PromptTemplate
except Exception:
    try:
        from langchain import PromptTemplate
    except Exception as e:
        raise ImportError("Could not import PromptTemplate from langchain. Try installing a compatible langchain version.") from e

# ChatOpenAI client (langchain-openai package)
try:
    from langchain_openai import ChatOpenAI
except Exception as e:
    raise ImportError("langchain_openai.ChatOpenAI import failed. Install the package: pip install langchain-openai") from e

# local modules - ensure these files exist (as provided earlier)
from agents.langchain_tools import (
    parse_product_tool,
    build_question_chain,
    build_blocks_chain,
    build_page_render_chain,
)
from agents.utils import load_assignment_product, write_json


def make_llm():
    """
    Create a deterministic chat LLM. Set env PREFERRED_MODEL to override model.
    """
    preferred = os.environ.get("PREFERRED_MODEL", "gpt-4o-mini")
    # ChatOpenAI signature may differ between versions; this is the common one.
    try:
        return ChatOpenAI(model=preferred, temperature=0.0)
    except TypeError:
        # older ChatOpenAI used 'model_name' parameter
        return ChatOpenAI(model_name=preferred, temperature=0.0)


def run_chain(chain: LLMChain, **kwargs) -> str:
    """
    Safe runner for an LLMChain. Returns raw LLM string output.
    """
    # LLMChain.run is the usual API. If unavailable, try calling chain.predict.
    if hasattr(chain, "run"):
        return chain.run(**kwargs)
    elif hasattr(chain, "predict"):
        return chain.predict(**kwargs)
    else:
        raise RuntimeError("LLMChain has neither run() nor predict() methods.")


def main():
    print("LangChain orchestrator (robust) starting...")

    llm = make_llm()
    print("Using LLM:", getattr(llm, "model", getattr(llm, "model_name", "ChatOpenAI")))

    # 1. deterministic parse
    raw = load_assignment_product()
    product_model = parse_product_tool(raw)
    print("Parsed product:", product_model["name"])

    # 2. build chains
    question_chain = build_question_chain(llm)
    blocks_chain = build_blocks_chain(llm)
    product_render_chain = build_page_render_chain(llm, "product")
    faq_render_chain = build_page_render_chain(llm, "faq")
    comparison_render_chain = build_page_render_chain(llm, "comparison")

    # 3. run question chain
    print("-> Generating questions (LLM chain)")
    questions_raw = run_chain(question_chain, product_json=json.dumps(product_model, ensure_ascii=False), min_questions=15)
    try:
        questions = json.loads(questions_raw)
    except Exception:
        print("Failed to parse questions JSON. Raw output:")
        print(questions_raw)
        raise

    print(f"Generated {len(questions)} questions")

    # 4. run blocks chain
    print("-> Generating content blocks (LLM chain)")
    blocks_raw = run_chain(blocks_chain, product_json=json.dumps(product_model, ensure_ascii=False))
    try:
        blocks = json.loads(blocks_raw)
    except Exception:
        print("Failed to parse blocks JSON. Raw output:")
        print(blocks_raw)
        raise

    print("Blocks keys:", list(blocks.keys()))

    # 5. render product page
    print("-> Rendering product page")
    prod_out = run_chain(product_render_chain, product_json=json.dumps(product_model, ensure_ascii=False), blocks_json=json.dumps(blocks, ensure_ascii=False), questions_json="[]", product_b_json="{}")
    try:
        prod_page = json.loads(prod_out)
    except Exception:
        print("Product page render invalid JSON. Raw output:")
        print(prod_out)
        raise
    write_json("product_page.json", prod_page)

    # 6. render FAQ page
    print("-> Rendering FAQ page")
    faq_out = run_chain(faq_render_chain, product_json=json.dumps(product_model, ensure_ascii=False), blocks_json=json.dumps(blocks, ensure_ascii=False), questions_json=json.dumps(questions, ensure_ascii=False), product_b_json="{}")
    try:
        faq_page = json.loads(faq_out)
    except Exception:
        print("FAQ render invalid JSON. Raw output:")
        print(faq_out)
        raise
    write_json("faq.json", faq_page)

    # 7. comparison
    product_b = {
        "name": "DermaRadiance Serum",
        "concentration": "12% Vitamin C",
        "skin_type": ["Oily"],
        "ingredients": ["Vitamin C", "Niacinamide"],
        "benefits": ["Brightening", "Oil balancing"],
        "how_to_use": "Apply 2–3 drops in the morning; follow with moisturizer.",
        "side_effects": "May cause mild tingling for sensitive skin.",
        "price": 799,
    }

    print("-> Rendering comparison page")
    comp_out = run_chain(comparison_render_chain, product_json=json.dumps(product_model, ensure_ascii=False), blocks_json=json.dumps(blocks, ensure_ascii=False), questions_json="[]", product_b_json=json.dumps(product_b, ensure_ascii=False))
    try:
        comp_page = json.loads(comp_out)
    except Exception:
        print("Comparison render invalid JSON. Raw output:")
        print(comp_out)
        raise
    write_json("comparison_page.json", comp_page)

    print("Done — outputs in ./output/ (product_page.json, faq.json, comparison_page.json)")


if __name__ == "__main__":
    main()


