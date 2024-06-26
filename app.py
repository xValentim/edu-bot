from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import streamlit as st
from utils import*




# LOGIN
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]: #Se as credenciais forem corretas abre o chatbot
    authenticator.logout(location='sidebar')
    
    #CHATBOT
    st.title("Assistente virtual - Pergunte ao EduBot")
    cs_sidebar()
    

    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Olá, eu sou o Edu Bot que foi desenvolvido pela Nero.AI. Estou aqui para responder perguntas sobre ENEM. Como posso ajudar você?"),
        ]

    if 'db' not in st.session_state:
        st.session_state.db = vector_db()
        st.session_state.retriever = st.session_state.db.as_retriever(search_kwargs={"k": 3})

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI", avatar="imgs/perfil.png"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human", avatar="👤"):
                st.write(message.content)

    # user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))

        with st.chat_message("Human", avatar="👤"):
            st.markdown(user_query)

        
        with st.chat_message("AI", avatar="imgs/perfil.png"):
            with st.spinner("Thinking..."):
                response = st.write_stream(respond(user_query, st.session_state.chat_history, st.session_state.db, st.session_state.retriever))
        st.session_state.chat_history.append(AIMessage(content=response))

elif st.session_state["authentication_status"] is False: # Se as credenciais forem falsas, gera o aviso
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
