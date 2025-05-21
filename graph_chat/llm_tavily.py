
import os

from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI


# TODO:(wwc, 2025-05-21): 自己申请llm key和检索key
# llm = ChatOpenAI(
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     api_key="",
#     model_name="qwen-plus-1220",
#     # model_name="qwq-plus",
#     temperature=0,
#     # streaming=True,
# )

llm = ChatOpenAI(
    base_url="https://c-z0-api-01.hash070.com/v1",
    api_key="",
    model_name="gpt-3.5-turbo",
    # model_name="qwq-plus",
    temperature=0,
    # streaming=True,
)
# 初始化搜索工具，限制结果数量为1
os.environ["TAVILY_API_KEY"] = ""
tavily_tool = TavilySearchResults(max_results=1)