# Project Documentation (LangChain-based)

## Problem Statement
(unchanged) Build a modular agentic automation system to convert a small product dataset into structured JSON pages (FAQ, product page, comparison). The assignment requires using an agent framework — LangChain is mandatory.

## Solution Overview
This implementation uses **LangChain** for agent orchestration. Tools are created to encapsulate single responsibilities:
- Deterministic parsing tool (pure Python)
- LLM-backed question generation tool
- LLM-backed content block generation tool
- LLM-backed page renderer tools (faq, product, comparison)

An agent executor (LangChain `initialize_agent`, `AgentType.ZERO_SHOT_REACT_DESCRIPTION`) orchestrates the pipeline by deciding which tools to call and in which order.

## Why LangChain
- LangChain provides established tooling for agent orchestration, tool invocation, and declarative tool descriptions.
- Using LangChain demonstrates practical engineering judgement: leverage mature libraries rather than re-implementing orchestration patterns.

## Agent/Tool Boundaries
- `parse_product` — deterministic normalization (no model).
- `question_generator` — LLM chain generating exactly N categorized questions, returns a JSON array.
- `content_blocks` — LLM chain producing summary, benefits, usage, safety as JSON.
- `render_product_page`, `render_faq_page`, `render_comparison_page` — LLM chains that create fully-structured JSON pages.

## Orchestration Flow (high-level)
The LangChain agent is given the toolset and a few high-level prompts. The model decides which tools to call. The orchestrator script coordinates the top-level calls and validates outputs before saving.

## Scopes & Assumptions
- Only the provided product dataset is used.
- Product B in comparisons is fictional and deterministic.
- LLM is instructed to rely only on provided product JSON for content (prompts enforce this).

## How to run
See README.md

## Extensibility
- Add more tools (e.g., SEO writer, translation tool).
- Swap LLM models by changing `make_llm()` in `agents/langchain_orchestrator.py`.

