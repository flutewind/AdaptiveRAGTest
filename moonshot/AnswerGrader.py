from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from CreateIndex.create_index import retriever

### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from utils.llm_factory import get_moonshot_llm


# Prompt
prompt = hub.pull("rlm/rag-prompt")

### Answer Grader


# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# LLM with function call
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm = get_moonshot_llm()
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

question = "agent memory"
docs = retriever.invoke(question)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
# docs_txt = format_docs(docs)
# generation = rag_chain.invoke({"context": docs_txt, "question": question})

answer_grader = answer_prompt | structured_llm_grader
# answer_grader.invoke({"question": question, "generation": generation})

#print(GradeAnswer(binary_score='yes'))
