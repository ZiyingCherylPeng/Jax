from database import store_conversation, get_conversations, get_button_label, get_messages

print(get_conversations("249aea67-a3d0-4a38-ab29-aadcc38dbbee"))

# conversations = get_conversations("249aea67-a3d0-4a38-ab29-aadcc38dbbee")
# for conversation in conversations:
#     print(get_messages(conversation))



# def split(message):
#     return ' '.join(message.split()[:5])

# print(split("What actors or actresses play the same character in almost every movie or show they do?"))

# import streamlit as st

# st.markdown(
#     """
#     <style>
#     .fixed-size-button {
#         width: 500px;
#         height: 50px;
#         background-color: red;
#         color: white;
#         border: none;
#         font-size: 16px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # if st.button("Fixed Size Button", key="fixed_size"):
# #     st.write("Button clicked!")


# st.markdown('<button class="fixed-size-button">Fixed Size Button</button>', unsafe_allow_html=True)

