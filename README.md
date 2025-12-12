# Kasparro – Multi-Agent Content Generation System  
### Applicant: **MD SHAFI AZAM**

This repository implements the **Applied AI Engineer: Multi-Agent Content Generation System** assignment from **Kasparro**.  
It includes:

- A **LangChain-based agentic pipeline** (as required by the assignment)  
- A **deterministic mock orchestrator** for environments where LangChain installation is not possible  
- Modular agents, reusable blocks, templates, and fully JSON-structured outputs

---

# 📌 Assignment Goals (Summary)

Using ONLY the given product dataset (GlowBoost Vitamin C Serum), the system must:

- Parse input into an internal product model  
- Generate **15 categorized questions**  
- Create **reusable logic blocks**  
- Assemble **FAQ Page**, **Product Page**, **Comparison Page**  
- Output all results in **clean JSON**  
- Use **multi-agent orchestration**  
- Use **LangChain (required)** for agent frameworks  
- Provide a modular, extensible architecture  

---

# 🧠 System Overview

This repo contains **two runnable pipelines**:

## 1️⃣ LangChain Agentic Pipeline *(Primary – For Reviewers)*  
Located in:
agents/langchain_orchestrator.py
agents/langchain_tools.py


This pipeline uses:

- `langchain==0.0.350`
- `langchain-openai==0.0.8`
- `initialize_agent` + `Tool` API  
- LLM-backed agents for:
  - Question generation  
  - Content block generation  
  - JSON template rendering  

This pipeline **cannot run in some local Windows setups** due to PyPI version inconsistencies, so reviewers are provided with **instructions to run it in GitHub Codespaces or Google Colab**, where package installation is clean and stable.

---

## 2️⃣ Deterministic Mock Orchestrator *(Guaranteed to Run Anywhere)*  
agents/run_mock_orchestrator.py


This is a fallback pipeline using:

- Pure Python  
- No external dependencies  
- No LangChain needed  
- Generates **the exact JSON outputs** required by the assignment  

This ensures the repository remains **fully functional and reviewable**, even if LangChain cannot be installed in the evaluator’s local environment.

---


---

# 🚀 Running the LangChain Pipeline (For Reviewers)

Because LangChain installation is frequently blocked in Windows environments, I provide **officially supported methods** to run the pipeline.

---

# ✔ Recommended: **Run in GitHub Codespaces**

1. Open this repository in GitHub  
2. Click **Code → Open with Codespaces → New Codespace**  
3. In the Codespace terminal run:

```bash
pip install --upgrade pip
pip install "langchain==0.0.350" "langchain-openai==0.0.8" openai python-dotenv







