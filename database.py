import psycopg2
from psycopg2 import pool
import uuid
from datetime import datetime
import streamlit as st

# Create a connection pool
def create_connection_pool():
    return psycopg2.pool.SimpleConnectionPool(
        1,  
        20,  
        dbname=st.secrets["DBNAME_CONVERSATION"],
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
        if exc_type:  
            self.conn.rollback()  
        else:
            self.conn.commit()  

        self.cursor.close() 
        if self.conn:
            try:
                self.connection_pool.putconn(self.conn, close=True)  
            except Exception as e:
                print(f"Error returning connection to pool: {e}")  


connection_pool = create_connection_pool()


def store_conversation(conversation_id, user_id, timestamp, message_type, message_content):
    with DatabaseConnection(connection_pool) as cursor:
        cursor.execute('''
            INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
            VALUES (%s, %s, %s, %s, %s)
        ''', (conversation_id, user_id, datetime.now(), message_type, message_content))
        cursor.connection.commit()

# Get the most recent conversations for a user
def get_conversations(user_id, limit=5):
    with DatabaseConnection(connection_pool) as cursor:
        cursor.execute('''
            SELECT conversation_id
            FROM chat_history
            WHERE user_id = %s
            GROUP BY conversation_id
            ORDER BY MAX(timestamp) DESC
            LIMIT %s;
        ''', (user_id, limit))
        return cursor.fetchall()

def get_messages(conversation_id):
    with DatabaseConnection(connection_pool) as cursor:
        cursor.execute('''
            SELECT message_type, message_content 
            FROM chat_history
            WHERE conversation_id = %s
            ORDER BY timestamp 
        ''', (conversation_id,))
        return cursor.fetchall()

def get_button_label(conversation_id):
    message_content = get_messages(conversation_id)
    return f"Chat: {' '.join(message_content[0][1].split()[:5])}{'...'}"


# def get_button_label(conversation_id, message_content):
#     return f"Chat:{conversation_id[:5]}:{' '.join(message_content.split()[:7])}{'...'}"
