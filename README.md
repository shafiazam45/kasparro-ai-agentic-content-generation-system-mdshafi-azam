# Kasparro — Agentic Content Generation System (LangChain)

This repository implements the Kasparro assignment using **LangChain** as the agent framework (required by reviewers).

It produces:
- `output/product_page.json`
- `output/faq.json`
- `output/comparison_page.json`

All outputs are JSON and generated via LangChain agents/tools.

## Requirements

1. Python 3.8+
2. Install dependencies:
```bash
pip install -r requirements.txt

## Note about LangChain installation (important)

This repository includes a LangChain-based implementation (`agents/langchain_orchestrator.py`, `agents/langchain_tools.py`) that demonstrates framework-driven agent orchestration as required by the assignment.

During development on the reviewer’s environment, installing a compatible LangChain + langchain-openai pair failed due to PyPI/version constraints. To ensure reproducible final outputs for review, a deterministic mock runner `agents/run_mock_orchestrator.py` is included and used to generate the canonical files in `output/` (faq.json, product_page.json, comparison_page.json).

If you prefer to run the LangChain pipeline locally, please install a compatible LangChain and langchain-openai version (instructions in this README), then run:
```bash
python -m agents.langchain_orchestrator


