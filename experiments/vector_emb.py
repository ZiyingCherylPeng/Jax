from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
import psycopg2
from langchain_openai import AzureOpenAIEmbeddings
import streamlit as st
import urllib.parse
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import AzureChatOpenAI, ChatOpenAI


# def get_connection_uri():
#     # Read URI parameters from the environment
#     dbhost = st.secrets['DBHOST']
#     dbname = st.secrets['DBNAME_VECTOR']
#     dbuser = urllib.parse.quote(st.secrets['DBUSER'])
#     password = st.secrets['DBPASSWORD']
#     sslmode = st.secrets['SSLMODE']

#     # Construct connection URI
#     db_uri = f"postgresql://{dbuser}:{password}@{dbhost}/{dbname}?sslmode={sslmode}"
#     return db_uri

# print("the url:", get_connection_uri())
# loader = PyPDFLoader("../documents/Cayenta Time Manager Handout with Icons Replaced.pdf")
# documents = loader.load_and_split()
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size = 500, 
#     chunk_overlap = 100
# )

# docs = text_splitter.split_documents(documents)
# vectorstore.add_documents(docs)


def setup_qa_chatin():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint="https://aais-cay-jax-p02.openai.azure.com/",
        api_key="cb9b2e2451eb4a639730e6e8ea111e68",
        azure_deployment="text-embedding-ada-002",
        openai_api_version="2023-05-15",
    )

    # connection = get_connection_uri()
    connection = "postgresql://pgamin:JtGzPA8w5FH<Y>96M#+k@psql-cay-jax-p01.postgres.database.azure.com/pgvector?sslmode=require"

    collection_name = "Time_Entry"

    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )

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
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        output_key='answer',
        return_messages=True
    )
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    return qa_chain

qa_chain = setup_qa_chatin()
response=qa_chain.invoke({"question":"can i menually enter time?"})
print(response)
def print_result(response):
    if 'source_documents' in response and response['source_documents']:
        print("Checking the structure of source documents:")
        for doc in response['source_documents']:
            print("Document content:")
            print(doc)  
print_result(response)