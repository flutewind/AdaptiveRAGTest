from pprint import pprint

from langchain.schema import Document
# from openai.types.responses import web_search_tool
from langchain_community.tools.tavily_search import TavilySearchResults

from moonshot.AnswerGrader import format_docs, rag_chain, answer_grader
from moonshot.HallucinationGrader import hallucination_grader
from moonshot.QuestionRewriting import question_rewriter
from moonshot.RetrievalGrader import retrieval_grader
from CreateIndex.create_index import retriever
from moonshot.router import question_router

# from tongyi.AnswerGrader import answer_grader
# from tongyi.HallucinationGrader import hallucination_grader
# from tongyi.QuestionRewriting import question_rewriter
# from tongyi.RetrievalGrader import retrieval_grader
# from tongyi.create_index import retriever
# from tongyi.generate import format_docs, rag_chain
# from tongyi.router import question_router

def give_up(state):
    if "generation" in state:
        return {"generation": state["generation"]}
    return {"generation": "Sorry, I couldn't find a definitive answer to your question."}

def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question, "retries": 0, "gen_retries": 0}


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    docs_txt = format_docs(documents)
    generation = rag_chain.invoke({"context": docs_txt, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        print(f"Document score: {score}")
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """
    global_retries = state.get("global_retries", 0)
    if global_retries >= 2:
        # 强制终结
        return "give_up"

    state["global_retries"] = global_retries + 1

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}


def web_search(state):
    print("---WEB SEARCH---")
    question = state["question"]
    web_search_tool = TavilySearchResults(k=3)
    docs = web_search_tool.invoke({"query": question})
    # 变成 Document 列表
    web_results = [
        Document(page_content=d["content"], metadata={"url": d["url"]})
        for d in docs
        if d.get("content")
    ]
    return {"documents": web_results, "question": question}

### Edges ###


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    state["global_retries"] = 0

    if source is None:                       # 新增
        print("---ROUTER RETURNED None, DEFAULT TO RAG---")
        return "vectorstore"

    data_source = getattr(source, "datasource", None)
    if data_source == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    else:
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    global_retries = state.get("global_retries", 0)
    if global_retries >= 3:  # 全局最多 3 次
        return "give_up"

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        state["global_retries"] = global_retries + 1
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    global_retries = state.get("global_retries", 0)
    if global_retries >= 3:
        return "give_up"

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    gen_retries = state.get("gen_retries", 0)

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        if gen_retries >= 2:  # 最多重试 2 次
            print("---DECISION: REPEATED RETRIES STILL NO, RETURN---")
            return "give_up"
        state["gen_retries"] = gen_retries + 1
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
