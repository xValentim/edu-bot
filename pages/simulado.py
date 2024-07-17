import streamlit as st
from streamlit import session_state as ss
from utils import*
from modules.nav import MenuButtons

if 'authentication_status' not in ss:
    st.switch_page('./pages/account.py')

MenuButtons()

#CHATBOT
st.title("Gerador de Simulados - EduBot")
cs_sidebar()

def gera_simulado(user_query):
    
    template = f"""Você é um assistente de modelo de linguagem de IA que irá gerar simulados. Sua tarefa é separar cada uma das matérias ou temas
    que o usuário deseja estudar. A entrada do usuário pode ter uma ou mais matérias ou temas.
    Forneça esses temas/matérias separados por novas linhas. \n
    Separe os temas em: {user_query} \n
    Saída (4 consultas):"""


    # prompt_rag_temas = ChatPromptTemplate.from_template(template)

    # generate_temas = (
    #     prompt_rag_temas 
    #     | ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-0125")
    #     | StrOutputParser() 
    #     | (lambda x: x.split("\n"))
    # )

    # #Chain com RRF

    
    # template_1 = [
    #     ('system', """
    #                 Você é um bot chamado Edu e foi desenvolvido pela Nero.AI. 
    #                 Você irá gerar questões para compor um simulado do ENEM."""),
    #     ('system', "Use essas questões como exemplo de estrutura de questão e como formular um raciocínio\n\n{context_query}\n\n"),
    #             ('system', """Exiba as questões na estrutura:
    #              Tema: (tema_questao)
    #              QUESTÃO 1: (questao_1)
    #              a) alternativa 1
    #              b) alternativa 2
    #              c) alternativa 3
    #              d) alternativa 4
    #              e) alternativa 5

    #              QUESTÃO 2: (questao_2)
    #              a) alternativa 1
    #              b) alternativa 2
    #              c) alternativa 3
    #              d) alternativa 4
    #              e) alternativa 5

    #              e assim por diante.
    #              """),
    #     ('system', "Gere 5 questões sobre o tema: {tema_questao}"),
    # ]
    
    # prompt1 = ChatPromptTemplate.from_messages(template_1)
    
    
    # llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-0125")
    

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-0125")

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.stream({})


st.subheader("Esta é a ferramenta para gerar simulados para o ENEM. Sobre quais matérias e temas você deseja gerar as questões?")

tema = st.text_input("Insira as matérias e temas desejados")

button_correcao = st.button("Gerar", type="primary")
if button_correcao:
    with st.chat_message("Human", avatar="imgs/perfil.png"):
        st.write_stream(gera_simulado(tema))