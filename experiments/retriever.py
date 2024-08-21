from vector_emb import vectorstore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import Runnable
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

llm = AzureChatOpenAI(
    azure_endpoint="https://aais-cay-jax-p02.openai.azure.com/",
    api_key="cb9b2e2451eb4a639730e6e8ea111e68",
    azure_deployment="gpt-4o-mini",
    openai_api_version="2023-05-15",
    )

retriever = vectorstore.as_retriever(
    search_type = "similarity",
    search_kwargs={'k': 3},
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
# print(rag_chain.invoke({"input":"What is Time Entry?"}))

# QUESTION_PROMPT  = ChatPromptTemplate.from_template("""
#     Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.
#     This is a conversation with a human. Answer the questions you get based on the knowledge you have.
#     If you don't know the answer, just say that you don't, don't try to make up an answer.

#     Chat History:
#     {chat_history}
#     Follow Up Input: {question}
#     Standalone question:
#     """)



# qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever,
#                                             condense_question_prompt=QUESTION_PROMPT,
#                                             return_source_documents=True, verbose=False)
# chat_history = """
# """
# question = "What is Time Entry?"

# # Invoke the chain and print the output
# result = qa.invoke({"question": question, "chat_history": chat_history})
# print(result)


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

print(conversational_rag_chain.invoke({"input":"Can you manually input time?"}))
