import uuid
import agent_chain as agent
import streamlit as st
from PIL import Image

ALLOWED_IMAGE_TYPES = ["jpg", "png", "jpeg"]
ERROR_MESSAGE = "すみません、エラーが発生しました。エージェントサーバーのログをご確認ください。"

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_image_upload(uploaded_file):
    if uploaded_file:
        image = Image.open(uploaded_file)
        # カラム幅を調整して画像を表示
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="アップロードされた画像", use_container_width=True)

def add_message_to_history(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    with st.chat_message(role):
        st.markdown(content)

def process_user_input(user_input, thread_id, uploaded_file):
    try:
        _, bot_response = agent.call_agent(user_input, thread_id, uploaded_file)
    except Exception as e:
        print("thread_id:", thread_id)
        print("エラー:", e)
        return ERROR_MESSAGE
    return bot_response

def main():
    st.title("経費精算エージェント")
    initialize_session()
    display_chat_history()

    user_input = st.chat_input("メッセージを入力してください")
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=ALLOWED_IMAGE_TYPES)
    thread_id = uuid.uuid4()
    if uploaded_file:
        handle_image_upload(uploaded_file)

    if user_input:
        add_message_to_history("user", user_input)
        bot_response = process_user_input(user_input, thread_id, uploaded_file)
        add_message_to_history("assistant", bot_response)

if __name__ == "__main__":
    main()