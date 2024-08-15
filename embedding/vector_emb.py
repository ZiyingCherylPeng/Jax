from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
import psycopg2
from langchain_openai import AzureOpenAIEmbeddings
import streamlit as st
import urllib.parse

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

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint="https://aais-cay-jax-p02.openai.azure.com/",
    api_key="cb9b2e2451eb4a639730e6e8ea111e68",
    azure_deployment="text-embedding-ada-002",
    openai_api_version="2023-05-15",
)

# connection = get_connection_uri()
connection = "postgresql://pgamin:JtGzPA8w5FH<Y>96M#+k@psql-cay-jax-p01.postgres.database.azure.com/pgvector?sslmode=require"

collection_name = "time_manager"

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

loader = PyPDFLoader("../documents/Cayenta Time Manager Handout with Icons Replaced.pdf")
documents = loader.load_and_split()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500, 
    chunk_overlap = 100
)

docs = text_splitter.split_documents(documents)
vectorstore.add_documents(docs)


