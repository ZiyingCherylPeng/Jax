from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from login import login_ui
import streamlit as st
from datetime import datetime
import uuid
from database_api import store_conversation, get_conversations, get_messages, get_button_label
from vector_api import load_data, split_document, make_embeddings, make_vectorstore, make_chain, build_retriever, vectorstore_exists, load_existing_vectorstore, process_files
import os
from streamlit_extras.stoggle import stoggle

# def init_rag_chain():
#     # data = load_data("./documents/Cayenta Time Manager Handout with Icons Replaced.pdf")
#     if "rag_chain" not in st.session_state: 
#         directory = "./documents/"
#         all_docs = process_files(directory)
#         embeddings = make_embeddings()
#         if not vectorstore_exists("Time_Entry"):
#             vectorstore = make_vectorstore(embeddings, 
#                                         st.secrets["PGVECTOR_CONNECTION_STRING"], 
#                                         "Time_Entry")
#         else:
#             vectorstore = load_existing_vectorstore("Time_Entry", st.secrets["PGVECTOR_CONNECTION_STRING"])
#             vectorstore.set_embeddings(embeddings) 
#         st.session_state.rag_chain = make_chain(all_docs,vectorstore)
#     return st.session_state.rag_chain


def init_rag_chain():
    directory = "./documents/"
    collection_name = "Time_Entry"
    if 'rag_chain' not in st.session_state:
        # all_docs = process_files(directory)
        embeddings = make_embeddings()
        vectorstore = make_vectorstore(embeddings, 
                                        st.secrets["PGVECTOR_CONNECTION_STRING"],
                                        collection_name)
        retriever = build_retriever(vectorstore)

        st.session_state['rag_chain'] = make_chain(retriever)
    return st.session_state['rag_chain']

rag_chain = init_rag_chain()

st.set_page_config(page_title="Jax", page_icon="🐶")

def main():
    
    if st.session_state.get("authenticated",False):
        
        st.title("🐶 I am Jax!")
        st.sidebar.write("Welcome,", st.session_state["display_name"])
        msgs = StreamlitChatMessageHistory()
        # memory = ConversationBufferMemory(
        #     chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
        # )

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


        if prompt := st.chat_input(placeholder="Tell me something about Cayenta."):
            st.chat_message("user").write(prompt)
            store_conversation(st.session_state["conversation_id"], st.session_state["user_id"],datetime.now(), 'human', prompt)
            
            # tools = [DuckDuckGoSearchRun(name="Search")]
            # chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
            # executor = AgentExecutor.from_agent_and_tools(
            #     agent=chat_agent,
            #     tools=tools,
            #     memory=memory,
            #     return_intermediate_steps=True,
            #     handle_parsing_errors=True,
            # )

            # with st.chat_message("assistant"):
            #     st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            #     cfg = RunnableConfig()
            #     cfg["callbacks"] = [st_cb]
            #     response = executor.invoke(prompt, cfg)
            #     st.write(response["output"])
            #     st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

            session_id = st.session_state["conversation_id"] 
            response = rag_chain.invoke({"question":prompt},
                                        config={"configurable":{"session_id":session_id}})
            
            msgs.add_user_message(prompt)
            with st.chat_message("assistant"):
                st.write(response['answer']) 
                msgs.add_ai_message(response['answer'])
                if 'source_documents' in response and response['source_documents']:
                    for doc in response['source_documents']:
                        # st.markdown(doc)
                        stoggle(summary="Citation", content=doc)

            store_conversation(st.session_state["conversation_id"], st.session_state["user_id"],datetime.now(), msg.type, response["answer"])

        st.sidebar.write("Chat History")
        conversations_id = get_conversations(st.session_state["user_id"], limit=5)
        for conversation_id in conversations_id:
            if st.sidebar.button(get_button_label(conversation_id[0])):
                msgs.clear()
                messages = get_messages(conversation_id[0])
                for message in messages:
                    if message[0] == 'human':
                        msgs.add_user_message(message[1])
                    else:
                        msgs.add_ai_message(message[1])
                st.session_state["conversation_id"] = conversation_id[0]
                st.rerun()
        
    else:
        login_ui()  

if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
    main()
