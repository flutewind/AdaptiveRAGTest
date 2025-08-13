### Search
#from langchain_community.tools.tavily_search import TavilySearchResults
#web_search_tool = TavilySearchResults(k=3)
from langchain_tavily import TavilySearch

web_search_tool = TavilySearch(max_results=3)   # 注意参数名变了

result = web_search_tool.invoke({"query": "What is the capital of China?"})
print(result)