# test_langchain_install.py
import sys
print("Python:", sys.version)
try:
    # Try a few import paths we used in the code
    print("Importing ChatOpenAI ...", end=" ")
    from langchain_openai import ChatOpenAI
    print("OK")
except Exception as e:
    print("FAILED:", type(e).__name__, e)

try:
    print("Importing LLMChain / PromptTemplate ...", end=" ")
    # try common import locations
    try:
        from langchain.chains import LLMChain
    except Exception:
        try:
            from langchain.chains.llm import LLMChain
        except Exception:
            from langchain.llms import LLMChain  # fallback
    from langchain.prompts import PromptTemplate
    print("OK")
except Exception as e:
    print("FAILED:", type(e).__name__, e)
