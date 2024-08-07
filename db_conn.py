import psycopg2
import uuid
from datetime import datetime
import streamlit as st

conn = psycopg2.connect(
    dbname=st.secrets["DBNAME"],
    user=st.secrets["DBUSER"],
    password=st.secrets["DBPASSWORD"],
    host=st.secrets["DBHOST"],
    port='5432')


cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id SERIAL PRIMARY KEY,
        conversation_id UUID,
        user_id TEXT,
        timestamp TIMESTAMPTZ,
        message_type TEXT,
        message_content TEXT
    )
''')
conn.commit()
