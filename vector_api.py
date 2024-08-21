from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import streamlit as st
from langchain_postgres import PGVector
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever, ConversationalRetrievalChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import psycopg2
from psycopg2 import pool
from langchain.memory import ConversationBufferMemory
import os

def create_connection_pool():
    return psycopg2.pool.SimpleConnectionPool(
        1,  
        20,  
        dbname=st.secrets["DBNAME_VECTOR"],
        user=st.secrets["DBUSER"],
        password=st.secrets["DBPASSWORD"],
        host=st.secrets["DBHOST"],
        port='5432'
    )

# Define a class to manage database connections
class DatabaseConnection:
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = self.connection_pool.getconn()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection_pool.putconn(self.conn)

connection_pool = create_connection_pool()

def vectorstore_exists(collection_name):
    with DatabaseConnection(connection_pool) as cursor:
        try:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM langchain_pg_collection WHERE name = %s)", (collection_name,))
            exists = cursor.fetchone()[0]
            return exists
        except Exception as e:
            st.error(f"Database query failed: {e}")
            return False


def load_existing_vectorstore(collection_name, connection_string,embeddings):
    try:
        vectorstore = PGVector(
            embeddings=embeddings, 
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True
        )
        return vectorstore
    except Exception as e:
        st.error(f"Failed to load vectorstore: {e}")
        return None
    
 

def load_data(path):
    loader = PyPDFLoader(path)
    data = loader.load_and_split()
    return data
    
def split_document(data):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500, 
        chunk_overlap = 100
    )
    doc = text_splitter.split_documents(data)
    return doc

def process_files(directory):
    all_docs = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            data = load_data(file_path)
            doc = split_document(data)
            all_docs.extend(doc)
    return all_docs   

def make_embeddings():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=st.secrets['AZURE_ENDPOINT'],
        api_key=st.secrets['OPENAI_API_KEY'],
        azure_deployment="text-embedding-ada-002",
        openai_api_version=st.secrets['OPENAI_API_VERSION'],)
    return embeddings

def make_vectorstore(embeddings, connection, collection_name):
    # connection = "postgresql://pgamin:JtGzPA8w5FH<Y>96M#+k@psql-cay-jax-p01.postgres.database.azure.com/pgvector?sslmode=require"
    # collection_name = "time_manager"
    # print("Embeddings object:", embeddings) 
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vectorstore

def build_retriever(vectorstore):
    retriever = vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs={'k': 3},)
    return retriever    

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]
    


def make_chain(retriever):
    # vectorstore.add_documents(doc)
    # retriever = build_retriever(vectorstore)
    llm = AzureChatOpenAI(
        azure_endpoint=st.secrets['AZURE_ENDPOINT'],
        api_key=st.secrets['OPENAI_API_KEY'],
        azure_deployment="gpt-4o-mini",
        openai_api_version=st.secrets['OPENAI_API_VERSION'])    
    
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        output_key='answer',
        return_messages=True,
    )
    conversational_rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    
    return conversational_rag_chain

#     contextualize_q_system_prompt = (
#     "Given a chat history and the latest user question "
#     "which might reference context in the chat history, "
#     "formulate a standalone question which can be understood "
#     "without the chat history. Do NOT answer the question, "
#     "just reformulate it if needed and otherwise return it as is."
# )

#     contextualize_q_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", contextualize_q_system_prompt),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}"),
#         ]
#     )

#     history_aware_retriever = create_history_aware_retriever(
#         llm, retriever, contextualize_q_prompt
#     )

#     system_prompt = (
#         "You are an assistant for question-answering tasks. "
#         "Use the following pieces of retrieved context to answer "
#         "the question. If you don't know the answer, say that you "
#         "don't know. Use five sentences maximum and keep the "
#         "answer concise."
#         "\n\n"
#         "{context}")
    
#     prompt = ChatPromptTemplate.from_messages(
#         [("system", system_prompt),
#          MessagesPlaceholder("chat_history"),
#          ("human", "{input}"),])
    
#     question_answer_chain = create_stuff_documents_chain(llm, prompt)
#     rag_chain = create_retrieval_chain(
#         history_aware_retriever, 
#         question_answer_chain,
#         return_source_documents=True)

#     conversational_rag_chain = RunnableWithMessageHistory(
#         rag_chain,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#         output_messages_key="answer",)


    



