from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError) 
from utils import *

def reset_conversation():
    st.session_state.chat_history = None

# Cria o authenticator 
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# LOGIN
try:
    authenticator.login(clear_on_submit=True)
except LoginError as e:
    st.error(e)

if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

if st.session_state["authentication_status"]: # Se as credenciais forem corretas abre o chatbot
    authenticator.logout(location='sidebar')
    cs_sidebar()
    


    page = st.sidebar.selectbox(
        "Navegar para:",
        ["Chatbot", "Redação"]
    )

    if page == "Chatbot":
        # Título do aplicativo
        st.title("Assistente virtual - Pergunte ao EduBot")
        st.subheader("Chatbot")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                AIMessage(content="Olá, eu sou o Edu Bot que foi desenvolvido pela Nero.AI. Estou aqui para responder perguntas sobre ENEM. Como posso ajudar você?"),
            ]

        if 'db' not in st.session_state:
            st.session_state.db = vector_db()
            st.session_state.retriever = st.session_state.db.as_retriever(search_kwargs={"k": 3})

        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI", avatar="imgs/perfil.png"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human", avatar="👤"):
                    st.write(message.content)

        # Entrada do usuário
        user_query = st.chat_input("Digite sua mensagem aqui...")
        if user_query is not None and user_query != "":
            st.session_state.chat_history.append(HumanMessage(content=user_query))

            with st.chat_message("Human", avatar="👤"):
                st.markdown(user_query)

            with st.chat_message("AI", avatar="imgs/perfil.png"):
                with st.spinner("Pensando..."):
                    response = st.write_stream(respond(user_query, st.session_state.chat_history, st.session_state.db, st.session_state.retriever))
            st.session_state.chat_history.append(AIMessage(content=response))

    elif page == "Redação":
        pg = st.navigation([st.Page("./pages/redacao.py")])
        pg.run()

elif st.session_state["authentication_status"] is False: # Se as credenciais forem falsas, gera o aviso
    st.error('Username/password is incorrect') 
elif st.session_state["authentication_status"] is None:
    if "chat_history" in st.session_state:
        st.session_state.pop("chat_history")
    st.warning('Please enter your username and password')
