"""
LangChain Tools definitions.

Each tool is single-responsibility and either deterministic (pure python) or
model-backed (LangChain LLMChain). Tools are wired into an AgentExecutor in orchestrator.
"""

from typing import Dict, Any, List
from langchain import LLMChain, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor  # used in orchestrator
from .utils import safe_parse_price
import json


# -------------------------
# Deterministic parsing tool
# -------------------------
def parse_product_tool(raw_product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic parsing: normalizes the raw fields into internal schema.
    This is a pure function and does not call the LLM.
    """
    model = {
        "name": raw_product["Product Name"].strip(),
        "concentration": raw_product["Concentration"].strip(),
        "skin_type": [t.strip() for t in raw_product["Skin Type"].split(",")],
        "ingredients": [i.strip() for i in raw_product["Key Ingredients"].split(",")],
        "benefits": [b.strip() for b in raw_product["Benefits"].split(",")],
        "how_to_use": raw_product["How to Use"].strip(),
        "side_effects": raw_product["Side Effects"].strip(),
        "price": safe_parse_price(raw_product["Price"]),
    }
    return model


# -------------------------
# LLM-based question generator
# -------------------------
def build_question_chain(llm: ChatOpenAI) -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["product_json", "min_questions"],
        template=(
            "You are a structured question generator. Given the product JSON below, "
            "produce EXACTLY {min_questions} user-facing Q&A questions (questions only, NO answers) "
            "as a JSON array of objects with fields: question, category. Categories should be"
            " one of: Informational, Usage, Safety, Purchase, Comparison, Ingredients. "
            "Be concise. Use only facts from the product JSON—do not invent new facts.\n\n"
            "PRODUCT_JSON:\n{product_json}\n\n"
            "Output only valid JSON."
        ),
    )
    return LLMChain(llm=llm, prompt=prompt)


def question_tool_factory(llm: ChatOpenAI, min_questions: int = 15) -> Tool:
    chain = build_question_chain(llm)

    def _run(product_model: Dict[str, Any]) -> str:
        product_json = json.dumps(product_model, ensure_ascii=False)
        out = chain.run(product_json=product_json, min_questions=min_questions)
        # Expect out to be JSON text; the agent will parse later.
        return out

    return Tool(name="question_generator", func=_run, description="Generate categorized user questions (JSON array).")


# -------------------------
# LLM-based content block generator
# -------------------------
def build_blocks_chain(llm: ChatOpenAI) -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["product_json"],
        template=(
            "You are a content-block generator. Given PRODUCT_JSON produce a JSON object with fields:\n"
            "- summary: a 1-2 sentence product summary (use product fields only)\n"
            "- benefits: array of benefit short bullets\n"
            "- usage: a short usage instruction (one line)\n"
            "- safety: a short safety note (one line)\n\n"
            "PRODUCT_JSON:\n{product_json}\n\n"
            "Rules:\n"
            "1) Use only the facts in PRODUCT_JSON.\n"
            "2) Output ONLY valid JSON (no surrounding commentary).\n"
            "3) Keep each field concise.\n"
        )
    )
    return LLMChain(llm=llm, prompt=prompt)


def blocks_tool_factory(llm: ChatOpenAI) -> Tool:
    chain = build_blocks_chain(llm)

    def _run(product_model: Dict[str, Any]) -> str:
        return chain.run(product_json=json.dumps(product_model, ensure_ascii=False))

    return Tool(name="content_blocks", func=_run, description="Generate content blocks JSON (summary, benefits, usage, safety).")


# -------------------------
# LLM-based template renderer -> produces full page JSON
# -------------------------
def build_page_render_chain(llm: ChatOpenAI, template_name: str) -> LLMChain:
    """
    template_name: one of 'faq', 'product', 'comparison'
    The prompt instructs the LLM to produce fully structured JSON for the given template.
    """
    if template_name == "faq":
        instr = (
            "Produce a JSON object: {\"product\": <name>, \"faqs\": [ {\"question\":..., \"answer\":..., \"category\":...}, ... ] }.\n"
            "Use the provided questions array and product/blocks to produce at least 5 Q&As. "
            "Answer content must be derived only from product/blocks. Output only JSON."
        )
    elif template_name == "product":
        instr = (
            "Produce a JSON object with fields: product_name, concentration, summary, key_ingredients (array), "
            "benefits (array), how_to_use, safety_info, price, skin_type (array). "
            "Use the provided product and blocks. Output only valid JSON."
        )
    elif template_name == "comparison":
        instr = (
            "Produce a JSON object comparing productA and productB. Include product_a, product_b and comparison object "
            "with price_diff string, ingredient_comparison (object with common, a_only, b_only arrays), "
            "and benefit_comparison (object with common, a_only, b_only arrays). Use only provided product data. Output only JSON."
        )
    else:
        raise ValueError("Unknown template")

    prompt = PromptTemplate(
        input_variables=["product_json", "blocks_json", "questions_json", "product_b_json"],
        template=(
            "You are a structured template renderer. {instr}\n\n"
            "PRODUCT_JSON:\n{product_json}\n\n"
            "BLOCKS_JSON:\n{blocks_json}\n\n"
            "QUESTIONS_JSON (may be empty for product/comparison templates):\n{questions_json}\n\n"
            "PRODUCT_B_JSON (for comparison template):\n{product_b_json}\n\n"
            "IMPORTANT: Output only valid JSON and adhere to the schema described.\n"
        ).replace("{instr}", instr)
    )

    return LLMChain(llm=llm, prompt=prompt)


def page_tool_factory(llm: ChatOpenAI, template_name: str) -> Tool:
    chain = build_page_render_chain(llm, template_name)

    def _run(args: Dict[str, Any]) -> str:
        # args expected to contain product_model (dict), blocks (dict), questions (list) optionally product_b
        product_json = json.dumps(args.get("product_model", {}), ensure_ascii=False)
        blocks_json = json.dumps(args.get("blocks", {}), ensure_ascii=False)
        questions_json = json.dumps(args.get("questions", []), ensure_ascii=False)
        product_b_json = json.dumps(args.get("product_b", {}), ensure_ascii=False)
        return chain.run(product_json=product_json, blocks_json=blocks_json, questions_json=questions_json, product_b_json=product_b_json)

    return Tool(name=f"render_{template_name}_page", func=_run, description=f"Render the {template_name} page JSON using product, blocks, and questions.")
