from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
import streamlit as st
from langchain_postgres import PGVector
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langcahin.memory import ConversationBufferMemory

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


def make_chain(doc,vectorstore):
    vectorstore.add_documents(doc)
    llm = AzureChatOpenAI(
        azure_endpoint=st.secrets['AZURE_ENDPOINT'],
        api_key=st.secrets['OPENAI_API_KEY'],
        azure_deployment="gpt-4o-mini",
        openai_api_version=st.secrets['OPENAI_API_VERSION'])
    retriever = build_retriever(vectorstore)
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}")
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt),
         ("human", "{input}"),])
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain
    



