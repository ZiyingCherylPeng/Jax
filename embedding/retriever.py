from vector_emb import vectorstore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import Runnable

llm = AzureChatOpenAI(
    azure_endpoint="https://aais-cay-jax-p02.openai.azure.com/",
    api_key="cb9b2e2451eb4a639730e6e8ea111e68",
    azure_deployment="gpt-4o-mini",
    openai_api_version="2023-05-15",
    )

retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs={'k': 1},
)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


print(rag_chain.invoke({"input":"What is Time Entry?"}))