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


def get_conversations(user_id, limit=5):
    cursor.execute('''
        SELECT DISTINCT conversation_id 
        FROM (
            SELECT conversation_id 
            FROM chat_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC
        ) AS ordered_chat_history
        LIMIT %s;
    ''', (user_id, limit))
    return cursor.fetchall()

def get_messages(conversation_id):
    cursor.execute('''
        SELECT message_type, message_content 
        FROM chat_history
        WHERE conversation_id = %s
        ORDER BY timestamp
    ''', (conversation_id,))
    return cursor.fetchall()

def get_button_label(conversation_id,messsage_content):
    return f"Chat:{conversation_id[0:5]}:{' '.join(messsage_content.split()[:5])}"

