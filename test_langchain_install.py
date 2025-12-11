# test_langchain_install.py

import sys
print("Python:", sys.version)

print("\n--- Testing ChatOpenAI import ---")
try:
    from langchain_openai import ChatOpenAI
    print("ChatOpenAI: OK")
except Exception as e:
    print("ChatOpenAI FAILED:", type(e).__name__, e)

print("\n--- Testing LLMChain + PromptTemplate imports ---")
try:
    # Trying new location
    from langchain.chains import LLMChain
    print("LLMChain (langchain.chains): OK")
except Exception:
    try:
        # Old fallback
        from langchain.chains.llm import LLMChain
        print("LLMChain (langchain.chains.llm): OK")
    except Exception:
        try:
            # Very old fallback
            from langchain.llms import LLMChain
            print("LLMChain (langchain.llms): OK")
        except Exception as e:
            print("LLMChain FAILED:", type(e).__name__, e)

try:
    from langchain.prompts import PromptTemplate
    print("PromptTemplate: OK")
except Exception as e:
    print("PromptTemplate FAILED:", type(e).__name__, e)
