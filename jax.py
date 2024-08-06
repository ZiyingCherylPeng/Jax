from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from login import login_ui
import streamlit as st

st.set_page_config(page_title="Jax", page_icon="🐶")

def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        st.title("🐶 I am Jax!")
        # st.sidebar.write("welcome")
        msgs = StreamlitChatMessageHistory()
        memory = ConversationBufferMemory(
            chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
        )
        if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
            msgs.clear()
            msgs.add_ai_message("How are you?")
            st.session_state.steps = {}

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

            llm = llm = AzureChatOpenAI(
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
    else:
        login_ui()  

if __name__ == "__main__":
    main()
