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

def store_conversation(conversation_id, user_id, datetime, message_type, message_content):
    cursor.execute('''
                    INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (conversation_id, user_id, datetime.now(), message_type, message_content))
    conn.commit()