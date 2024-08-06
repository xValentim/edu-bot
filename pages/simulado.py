import streamlit as st
from streamlit import session_state as ss
from langchain_core.runnables import RunnableParallel
from utils import*
from modules.nav import MenuButtons

if 'authentication_status' not in ss:
    st.switch_page('./pages/account.py')

MenuButtons()
cs_sidebar()
st.title("Gerador de Simulados - EduBot")


def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def format_questoes(questoes):
    return "\n\n".join([tema for tema in questoes])

def gera_simulado(user_query, retriever_simu, retriever):
    
    template = f"""Você é um assistente de modelo de linguagem de IA que irá gerar simulados. Sua tarefa é separar cada uma das matérias ou temas
    que o usuário deseja estudar e gerar uma curta query descrevendo o temas, para facilitar a busca por similaridade.
    A entrada do usuário pode ter uma ou mais matérias ou temas.
    Forneça esses temas/matérias separados por novas linhas, no formato:
    - Tema1: Descricao do tema1
    - Tema2: Descricao do tema2
    e assim por diante.
    Separe os temas em: {user_query}"""
    
    template_1 = [
        ('system', """
                    Você é um bot chamado Edu e foi desenvolvido pela Nero.AI. 
                    Você irá gerar questões para compor um simulado do ENEM."""),
        ('system', "Use essas questões como exemplo de estrutura de questão\n\n{context_query_simu}\n\n"),
        ('system', "Use esses documentos para embasar o conteúdo das questões\n\n{context_query_video}\n\n"),
        ('system', "Não crie questões unicamente objetivas, como 'O que é?', 'Quem foi?', contextualize breventemente o tema e crie questões que exijam raciocínio."),
        ('system', """Forneça essas perguntas alternativas separadas por novas linhas. \n:
            Siga a estrutura usando markdown:
            Tema: (tema_questao)\n
         
            QUESTÃO 1: (questao_1)\n
            a) alternativa 1
            b) alternativa 2
            c) alternativa 3
            d) alternativa 4
            e) alternativa 5

            QUESTÃO 2: (questao_2)
            a) alternativa 1
            b) alternativa 2
            c) alternativa 3
            d) alternativa 4
            e) alternativa 5

        e assim por diante.
            Gabarito: 1 - (letra correspondente a alternativa)\n
                      2 - (letra correspondente a alternativa)\n
        e assim por diante.
        """),
        ('system', "Gere 5 questões sobre o tema: {tema_questao}"),
    ]
    
    prompt1 = ChatPromptTemplate.from_messages(template_1)
    
    prompt = ChatPromptTemplate.from_template(template)

    llm = ChatOpenAI(temperature=0.1, model="gpt-4o")

    generate_temas = (
        prompt
        | llm
        | StrOutputParser()
        | (lambda x: x.split("\n"))
    )

    chain_rag_simu = retriever_simu | format_docs
    chain_rag_video = retriever | format_docs

    chain_rag = (
        {
            "context_query_simu": RunnablePassthrough() | chain_rag_simu,
            "context_query_video": RunnablePassthrough() | chain_rag_video,
            "tema_questao": RunnablePassthrough()
        }
        | prompt1
        | llm
        | StrOutputParser()
    )
    
    chain = generate_temas | chain_rag.map() | format_questoes | StrOutputParser()
    
    return chain.stream({})

st.subheader("Esta é a ferramenta para gerar simulados para o ENEM. Sobre quais matérias e temas você deseja gerar as questões?")

tema = st.text_input("Insira as matérias e temas desejados")

if 'db' not in st.session_state:
    st.session_state.db = vector_db()
    st.session_state.retriever = st.session_state.db.as_retriever(search_kwargs={"k": 3})

# if 'db_simu' not in st.session_state:
#     st.session_state.db_simu = vector_db_simu()
#     st.session_state.retriever_simu = st.session_state.db_simu.as_retriever(search_type="similarity", search_kwargs={"k": 3})

if 'control' not in st.session_state:
    username = ss["username"]
    with open(f'control.yaml') as file:
        control = yaml.load(file, Loader=SafeLoader)
    if username not in control:
        st.session_state.requests_used = 0
        control[username] = {"redacao_used": 0, "simulado_used": 0}
        with open(f'control.yaml', 'w') as file:
            yaml.dump(control, file)
    st.control = control

button_correcao = st.button("Gerar", type="primary")
if button_correcao:
    if st.control[username]["simulado_used"] >= 5:
        st.error("Você atingiu o limite de 5 pedidos de simulados.")
    else:
        with st.chat_message("Human", avatar="imgs/perfil.png"):
            st.write_stream(gera_simulado(tema, st.session_state.retriever, st.session_state.retriever))
        st.control[username]["simulado_used"] += 1
        with open(f'control.yaml', 'w') as file:
            yaml.dump(st.control, file)