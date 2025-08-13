# llm_factory.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.rate_limiters import InMemoryRateLimiter

_moonshot_llm = None

def get_moonshot_llm():
    global _moonshot_llm
    if _moonshot_llm is None:
        _moonshot_llm = ChatOpenAI(
            base_url="https://api.moonshot.cn/v1",
            api_key=os.getenv("MOONSHOT_API_KEY"),
            model="moonshot-v1-8k",
            rate_limiter=InMemoryRateLimiter(requests_per_second=0.05),
            temperature=0
        )
    return _moonshot_llm