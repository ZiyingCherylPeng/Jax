import urllib.parse
import streamlit as st

def get_connection_uri():

    # Read URI parameters from the environment
    dbhost = st.secrets['DBHOST']
    dbname = st.secrets['DBNAME_VECTOR']
    dbuser = urllib.parse.quote(st.secrets['DBUSER'])
    password = st.secrets['DBPASSWORD']
    sslmode = st.secrets['SSLMODE']

    # Construct connection URI
    db_uri = f"postgresql://{dbuser}:{password}@{dbhost}/{dbname}?sslmode={sslmode}"
    return db_uri

print("the url:", get_connection_uri())
