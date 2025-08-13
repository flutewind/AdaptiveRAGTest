from langchain_community.chat_models import ChatTongyi
from CreateIndex.create_index import retriever

### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
#llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
llm = ChatTongyi(model="qwen-turbo", temperature=0)

question = "agent memory"
docs = retriever.invoke(question)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs) if docs else ""

# Post-processing
def format_docs2(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
# docs_txt = format_docs(docs)
# generation = rag_chain.invoke({"context": docs_txt, "question": question})
# print(generation)
