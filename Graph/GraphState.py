from typing import List, Optional

from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation: str
    documents: List[str]
    datasource: Optional[str]
    retries: int  # 检索重试
    gen_retries: int  # 生成重试
    global_retries: int  # 全局计数器