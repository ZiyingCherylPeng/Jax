from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from login import login_ui
import streamlit as st
import psycopg2
from datetime import datetime
import psycopg2
import uuid
from datetime import datetime

conn = psycopg2.connect(
    dbname=st.secrets["DBNAME"],
    user=st.secrets["DBUSER"],
    password=st.secrets["DBPASSWORD"],
    host=st.secrets["DBHOST"],
    port='5432')

cursor = conn.cursor() 

st.set_page_config(page_title="Jax", page_icon="🐶")

def main():
    if st.session_state.get("authenticated",False):
        
        st.title("🐶 I am Jax!")
        st.sidebar.write("Welcome,", st.session_state["display_name"])
        # st.sidebar.write("Your id is:", st.session_state["user_id"])
        msgs = StreamlitChatMessageHistory()
        memory = ConversationBufferMemory(
            chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
        )

        if len(msgs.messages) == 0 or st.sidebar.button("New Chat"):
            msgs.clear()
            msgs.add_ai_message("How are you?")
            st.session_state.steps = {}
            st.session_state["conversation_id"] = str(uuid.uuid4())

        avatars = {"human": "user", "ai": "assistant"}
        for idx, msg in enumerate(msgs.messages):
            with st.chat_message(avatars[msg.type]):
                # Render intermediate steps if any were saved
                for step in st.session_state.steps.get(str(idx), []):
                    if step[0].tool == "_Exception":
                        continue
                    with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                        st.write(step[0].log)
                        st.write(step[1])
                st.write(msg.content)

                # store conversation history
                cursor.execute('''
                    INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (st.session_state["conversation_id"], st.session_state["user_id"], datetime.now(), msg.type, msg.content))
                conn.commit()


        if prompt := st.chat_input(placeholder="Tell me something about Cayenta."):
            st.chat_message("user").write(prompt)

            # 存储用户输入到数据库
            cursor.execute('''
                INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
                VALUES (%s, %s, %s, %s, %s)
            ''', (st.session_state["conversation_id"], st.session_state["user_id"], datetime.now(), 'human', prompt))
            conn.commit()

            llm = AzureChatOpenAI(
                azure_endpoint=st.secrets["AZURE_ENDPOINT"],
                openai_api_key=st.secrets["OPENAI_API_KEY"],
                azure_deployment=st.secrets["AZURE_DEPLOYMENT"],
                openai_api_version=st.secrets["OPENAI_API_VERSION"],
                )
            
            tools = [DuckDuckGoSearchRun(name="Search")]
            chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
            executor = AgentExecutor.from_agent_and_tools(
                agent=chat_agent,
                tools=tools,
                memory=memory,
                return_intermediate_steps=True,
                handle_parsing_errors=True,
            )
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                cfg = RunnableConfig()
                cfg["callbacks"] = [st_cb]
                response = executor.invoke(prompt, cfg)
                st.write(response["output"])
                st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

                # 存储AI回复到数据库
                cursor.execute('''
                    INSERT INTO chat_history (conversation_id, user_id, timestamp, message_type, message_content)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (st.session_state["conversation_id"], st.session_state["user_id"], datetime.now(), 'ai', response["output"]))
                conn.commit()


    else:
        login_ui()  

if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
    main()
