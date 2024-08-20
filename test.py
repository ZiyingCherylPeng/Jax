from database import store_conversation, get_conversations, get_button_label, get_messages
from database import store_conversation, get_conversations, get_messages, get_button_label
from vector import load_data, split_document, make_embeddings, make_vectorstore, make_chain, vectorstore_exists, load_existing_vectorstore
import os

# print(get_conversations("249aea67-a3d0-4a38-ab29-aadcc38dbbee"))

# massage = get_button_label("34d22480-00df-41a5-a0ee-f257e4dc15fd")
# print(massage)

def process_files(directory):
    all_docs = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            data = load_data(file_path)
            doc = split_document(data)
            all_docs.append(doc)
    return all_docs   


print(process_files("./documents/"))