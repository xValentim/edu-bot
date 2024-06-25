from dotenv import load_dotenv
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError) 

import os

# Langchain
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from pathlib import Path
import base64


from dotenv import load_dotenv

load_dotenv()

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def cs_sidebar():

    # st.sidebar.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=128 height=128>](https://www.upload.ventures/)'''.format(img_to_bytes("imgs/upload_logo.jpg")), unsafe_allow_html=True)
    st.sidebar.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=112 height=20>](https://neroai.com.br/)'''.format(img_to_bytes("imgs/neroai_logo.png")), unsafe_allow_html=True)
    st.sidebar.header('Powered by [Nero.AI](https://neroai.com.br/)')

    return None

def vector_db():
    index_name = os.getenv("PINECONE_INDEX_NAME")
    embeddings_size = 1536
    embeddings_model = 'text-embedding-ada-002'
    embeddings = OpenAIEmbeddings(model=embeddings_model)
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    return vectorstore

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Funções auxiliares
def get_strings_from_documents(documents):
    return [doc.page_content for doc in documents]

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def respond(user_query, chat_history, db, retriever):
    
    all_messages = [
        ('system', "Aqui está o que foi conversado até agora:\n\n" + \
                    "\n\n".join([msg.content for msg in chat_history[-4:]])),
        ('system', """
                    Você é um bot chamado Edu e foi desenvolvido pela Nero.AI. 
                    Você vai responder perguntas sobre Enem e dar dicas de estudo.
                    Se apresente e diga como você pode ajudar."""),
        ('system', "Aqui está o contexto adicional de videos no YouYube:\n\n{context_query}\n\nSempre que possível, cite fontes (dados do YouTube) de onde você está tirando a informação. Somente cite fontes dos documentos fornecidos acima."),
        ('system', "Obrigatoriamente tente relacionar o contexto da adicional com o contexto da pergunta. FORNEÇA LINKS para conteúdos que possam interessar ao usuários. JAMAIS USE LINKS QUE NÂO FORAM FORNECIDOS A VOCÊ."),
        ('system', "Responda as perguntas com uma linguagem Markdown"),
        ('system', "{query}"),
    ]
    
    prompt = ChatPromptTemplate.from_messages(all_messages)

    chain_rag = retriever | format_docs
    
    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-0125")
    
    chain = (
            {
                "context_query": itemgetter("query") | chain_rag,
                
                "query": itemgetter("query")
             }
            | prompt
            | llm
            | StrOutputParser()
        )
    
    return chain.stream({"query": user_query})

embedding_size = 1536
embedding_model = 'text-embedding-ada-002'
embeddings = OpenAIEmbeddings(model=embedding_model)



# Carrega o arquivo config
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Cria o authenticator 
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Cria a tela
try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]: #Se as credenciais forem corretas abre o chatbot
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')

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


