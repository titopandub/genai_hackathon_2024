import src.bootstrap as _
import streamlit as st
import uuid
import logging

from src.chain.chain_router import run
from src.lib.user import User

def append_user_history(message):
    st.chat_message("user").markdown(message)
    st.session_state.messages.append({"role": "user", "content": message})

def append_assistant_history(message):
    st.chat_message("assistant").markdown(message)
    st.session_state.messages.append({"role": "assistant", "content": message})

st.title("Vidio Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    token = None
    if st.query_params.get("token"):
        token = st.query_params.get("token")
    
    user = User()
    if not user.is_login():
        append_user_history(prompt)
        append_assistant_history("bye")
    else:
        if 'visit_id' not in st.session_state:
            st.session_state['visit_id'] = str(uuid.uuid4())

        append_user_history(prompt)

        context = {
            "user_id": user.id(),
            "visit_id": st.session_state['visit_id'],
            "user_gender": user.gender(),
            "user_age": user.age()
        }

        response = "Maaf, tampaknya ada kesalahan sistem yang tidak terduga saat memproses pertanyaan Anda. Bisa tolong coba kirimkan pertanyaan Anda lagi? Kami sangat menghargai kesabaran Anda dan berusaha keras untuk memperbaiki masalah ini secepat mungkin. Terima kasih!"

        try:
            response = run(context, prompt)
        except Exception as e:
            error_msg = str(e)
            logging.error(error_msg)

        append_assistant_history(response)

