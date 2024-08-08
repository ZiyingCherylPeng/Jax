from database import store_conversation, get_conversations, get_button_label, get_messages

print(get_conversations("249aea67-a3d0-4a38-ab29-aadcc38dbbee"))

conversations = get_conversations("249aea67-a3d0-4a38-ab29-aadcc38dbbee")
for conversation in conversations:
    print(get_messages(conversation))