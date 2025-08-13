from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi  # 使用通义千问
from pydantic import BaseModel, Field

# 设置 API Key（也可通过环境变量 DASHSCOPE_API_KEY 设置）
import os
os.environ["DASHSCOPE_API_KEY"] = "sk-b89af8c331144450816c06ec5a9aaf8e"

# 数据模型
class RouteQuery(BaseModel):
    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="选择将用户问题路由到向量数据库或网络搜索。",
    )

# 替换：使用通义千问模型
llm = ChatTongyi(model="qwen-max", temperature=0)  # 可选：qwen-plus, qwen-turbo
structured_llm_router = llm.with_structured_output(RouteQuery)

# 提示词
system = """你是一个专家，负责将用户问题路由到向量数据库或网络搜索。
向量数据库包含关于智能体、提示工程和对抗攻击的文档。
如果是这些主题，请使用向量数据库；否则使用网络搜索。"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router

# 测试
# print(question_router.invoke({"question": "熊队在NFL选秀中第一顺位选了谁？"}))
# print(question_router.invoke({"question": "智能体记忆有哪些类型？"}))