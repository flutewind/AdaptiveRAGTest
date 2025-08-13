from langgraph.graph import END, StateGraph, START

from Graph.GraphState import GraphState  # 直接导入类
from Graph.GraphFlow import web_search, retrieve, grade_documents, generate, transform_query, route_question, \
    decide_to_generate, grade_generation_v_documents_and_question

workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("transform_query", transform_query)  # transform_query
def give_up_answer(state):
    return {"generation": "Sorry, the current knowledge is not enough to answer this question."}

workflow.add_node("give_up", give_up_answer)
workflow.add_edge("give_up", END)

# Build graph
workflow.add_conditional_edges(
    START,
    route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
        "give_up": "give_up",
    },
)

# Compile
app = workflow.compile()