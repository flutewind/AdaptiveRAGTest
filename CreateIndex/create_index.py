import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import BSHTMLLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
### from langchain_cohere import CohereEmbeddings

from langchain_community.embeddings import DashScopeEmbeddings

embd = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("TONGYI_API_KEY")
)

# Docs to index
# 本地 HTML 文件路径
local_files = [
    "D:/company/data/2023-06-23-agent.html",
    "D:/company/data/2023-03-15-prompt-engineering.html",
    "D:/company/data/2023-10-25-adv-attack-llm.html"
]

# 加载本地 HTML 文件

# 指定 UTF-8 编码
docs = [BSHTMLLoader(file, open_encoding='utf-8').load() for file in local_files]
docs_list = [item for sublist in docs for item in sublist]

# Split
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

persist_dir = "./chroma_db"
if os.path.isdir(persist_dir) and os.listdir(persist_dir):
    # 目录已存在且有数据 → 直接加载
    vectorstore = Chroma(
        collection_name="rag-chroma",
        embedding_function=embd,
        persist_directory=persist_dir
    )
else:
    # 首次启动 → 重新建库
    docs = [BSHTMLLoader(f, open_encoding='utf-8').load() for f in local_files]
    docs_list = [i for s in docs for i in s]
    doc_splits = text_splitter.split_documents(docs_list)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        embedding=embd,
        collection_name="rag-chroma",
        persist_directory=persist_dir
    )
    vectorstore.persist()

# Add to vectorstore
# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=embd,
# )
retriever = vectorstore.as_retriever()