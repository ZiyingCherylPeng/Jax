# import psycopg2
# import uuid
# from datetime import datetime
# import streamlit as st

# conn = psycopg2.connect(
#     dbname=st.secrets["DBNAME_CONVERSATION"],
#     user=st.secrets["DBUSER"],
#     password=st.secrets["DBPASSWORD"],
#     host=st.secrets["DBHOST"],
#     port='5432')

# cursor = conn.cursor()

# def store_conversation(conversation_id, user_id, datetime, message_type, message_content):
#     cursor.execute('''
#                     INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
#                     VALUES (%s, %s, %s, %s, %s)
#                 ''', (conversation_id, user_id, datetime.now(), message_type, message_content))
#     conn.commit()


# def get_conversations(user_id, limit=5):
#     cursor.execute('''
#         SELECT DISTINCT conversation_id 
#         FROM (
#             SELECT conversation_id 
#             FROM chat_history 
#             WHERE user_id = %s 
#             ORDER BY timestamp DESC
#         ) AS ordered_chat_history
#         LIMIT %s;
#     ''', (user_id, limit))
#     return cursor.fetchall()

# def get_messages(conversation_id):
#     cursor.execute('''
#         SELECT message_type, message_content 
#         FROM chat_history
#         WHERE conversation_id = %s
#         ORDER BY timestamp 
#     ''', (conversation_id,))
#     return cursor.fetchall()

# def get_button_label(conversation_id,messsage_content):
#     return f"Chat:{conversation_id[:5]}:{' '.join(messsage_content.split()[:7])}{'...'}"

import psycopg2
from psycopg2 import pool
import uuid
from datetime import datetime
import streamlit as st

# 创建数据库连接池
def create_connection_pool():
    return psycopg2.pool.SimpleConnectionPool(
        1,  # 最小连接数
        10,  # 最大连接数
        dbname=st.secrets["DBNAME_CONVERSATION"],
        user=st.secrets["DBUSER"],
        password=st.secrets["DBPASSWORD"],
        host=st.secrets["DBHOST"],
        port='5432'
    )

# 使用上下文管理器自动处理连接和游标
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

def store_conversation(conversation_id, user_id, timestamp, message_type, message_content):
    with DatabaseConnection(connection_pool) as cursor:
        cursor.execute('''
            INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
            VALUES (%s, %s, %s, %s, %s)
        ''', (conversation_id, user_id, datetime.now(), message_type, message_content))
        cursor.connection.commit()


def get_conversations(user_id, limit=5):
    with DatabaseConnection(connection_pool) as cursor:
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
    with DatabaseConnection(connection_pool) as cursor:
        cursor.execute('''
            SELECT message_type, message_content 
            FROM chat_history
            WHERE conversation_id = %s
            ORDER BY timestamp 
        ''', (conversation_id,))
        return cursor.fetchall()

def get_button_label(conversation_id, message_content):
    return f"Chat:{conversation_id[:5]}:{' '.join(message_content.split()[:7])}{'...'}"
