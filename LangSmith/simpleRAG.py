from openai import OpenAI

openai_client = OpenAI(
    api_key="sk-bXX6MIIfpHdGybWbg9F1qO8yw3YAOY4eXsFHSZpgbieeEIqE",
    base_url="https://api.moonshot.cn/v1"
)
# This is the retriever we will use in RAG
# This is mocked out, but it could be anything we want
def retriever(query: str):
    results = ["Harrison worked at Kensho"]
    return results


# This is the end-to-end RAG chain.
# It does a retrieval step then calls OpenAI
def rag(question):
    docs = retriever(question)
    system_message = """Answer the users question using only the provided information below:

    {docs}""".format(docs="\n".join(docs))

    return openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        model="moonshot-v1-8k",
    )

print(rag("where did harrison work").choices[0].message.content)