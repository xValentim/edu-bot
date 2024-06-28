import streamlit as st
from utils import*
import streamlit as st
from PyPDF2 import PdfReader

st.title("EduBot - Correção de Redação")

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

uploaded_file = st.sidebar.file_uploader("Upload a file", type=['pdf'])
if uploaded_file is None:
    with st.chat_message("AI", avatar="imgs/perfil.png"):
        st.markdown("Faça o upload do arquivo PDF de sua redação!")
else:
    doc = PdfReader(uploaded_file)

    redacao = [doc.pages[i].extract_text() for i in range(len(doc.pages))]

    st.session_state.retriever = st.session_state.db.as_retriever(search_kwargs={"k": 3})

    #Chain com RRF
    chain_rag = st.session_state.retriever | format_docs

    # Rules
    base_rule = "Você é um corretor de redações do ENEM. Você irá corrigir a redação do usuário seguindo os critérios de correção do ENEM."
    rule_1 = """
        A 1a competência cobrada pela correção é: Domínio da escrita formal da língua portuguesa. Ela avalia se a redação do participante está 
        adequada às regras de ortografia, como acentuação, ortografia, uso de hífen, emprego de letras maiúsculas e minúsculas e separação silábica. 
        Ainda são analisadas a regência verbal e nominal, concordância verbal e nominal, pontuação, paralelismo, emprego de pronomes e crase.

        Nesta competência, o sistema de pontuação é dividido em seis níveis de desempenho, que são:

        - 0:  Demonstra desconhecimento da modalidade escrita formal da Língua Portuguesa.
        - 40: Demonstra domínio precário da modalidade escrita formal da Língua Portuguesa, de forma sistemática, com diversificados e 
            frequentes desvios gramaticais, de escolha de registro e de convenções da escrita.
        - 80: Demonstra domínio insuficiente da modalidade escrita formal da Língua, com muitos desvios gramaticais, de escolha de registro e de 
            convenções da escrita.
        - 120: Demonstra domínio mediano da modalidade escrita formal da Língua Portuguesa e de escolha de registro, com alguns desvios gramaticais 
            e de convenções da escrita.
        - 160: Demonstra bom domínio da modalidade escrita formal da Língua Portuguesa e de escolha de registro, com poucos desvios gramaticais 
            e de convenções da escrita.
        - 200: Demonstra excelente domínio da modalidade escrita formal da Língua Portuguesa e de escolha de registro. Desvios gramaticais ou de 
            convenções da escrita serão aceitos somente como excepcionalidade e quando não caracterizem reincidência.
    """
    rule_2 = """
        A 2a competência cobrada pela correção é: Compreender a proposta de redação e aplicar conceitos das várias áreas de conhecimento para 
        desenvolver o tema, dentro dos limites estruturais do texto dissertativo-argumentativo em prosa. Verifica se o candidato compreendeu a 
        proposta de redação e conseguiu desenvolver um texto dissertativo-argumentativo, utilizando conhecimentos de diferentes áreas.

        Nesta competência, o sistema de pontuação é dividido em seis níveis de desempenho, que são:

        - 0:  Fuga ao tema/não atendimento à estrutura dissertativo-argumentativa.
        - 40: Apresenta o assunto, tangenciando o tema, ou demonstra domínio precário do texto dissertativo-argumentativo, com traços constantes de outros tipos textuais.
        - 80: Desenvolve o tema recorrendo à cópia de trechos dos textos motivadores ou apresenta domínio insuficiente do texto dissertativo-argumentativo, não atendendo à estrutura com proposição, argumentação e conclusão.
        - 120: Desenvolve o tema por meio de argumentação previsível e apresenta domínio mediano do texto dissertativo- argumentativo, com proposição, argumentação e conclusão.
        - 160: Desenvolve o tema por meio de argumentação consistente e apresenta bom domínio do texto dissertativo-argumentativo, com proposição, argumentação e conclusão.
        - 200: Desenvolve o tema por meio de argumentação consistente, a partir de um repertório sociocultural produtivo, e apresenta excelente domínio do texto dissertativo-argumentativo.
    """
    rule_3 = """
        A 3a competência cobrada pela correção é: Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em 
        defesa de um ponto de vista. Avalia a capacidade do candidato de selecionar, relacionar e organizar informações, fatos, opiniões e 
        argumentos de forma coerente e coesa para defender seu ponto de vista.

        Nesta competência, o sistema de pontuação é dividido em seis níveis de desempenho, que são:

        - 0:  Ausência de marcas de articulação, resultando em fragmentação das ideias.
        - 40: Articula as partes do texto de forma precária.
        - 80: Articula as partes do texto, de forma insuficiente, com muitas inadequações e apresenta repertório limitado de recursos coesivos.
        - 120: Articula as partes do texto, de forma mediana, com inadequações e apresenta repertório pouco diversificado de recursos coesivos.
        - 160: Articula as partes do texto com poucas inadequações e apresenta repertório diversificado de recursos coesivos.
        - 200: Articula bem as partes do texto e apresenta repertório diversificado de recursos coesivos.
    """
    rule_4 = """
        A 4a competência cobrada pela correção é: Demonstrar conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. 
        Verifica o uso adequado de recursos linguísticos, como operadores argumentativos, modalizadores, conectivos, entre outros, para a construção da argumentação.

        Nesta competência, o sistema de pontuação é dividido em seis níveis de desempenho, que são:

        - 0:  Ausência de marcas de articulação, resultando em fragmentação das ideias.
        - 40: Articula as partes do texto de forma precária.
        - 80: Articula as partes do texto, de forma insuficiente, com muitas inadequações e apresenta repertório limitado de recursos coesivos.
        - 120: Articula as partes do texto, de forma mediana, com inadequações e apresenta repertório pouco diversificado de recursos coesivos.
        - 160: Articula as partes do texto com poucas inadequações e apresenta repertório diversificado de recursos coesivos.
        - 200: Articula bem as partes do texto e apresenta repertório diversificado de recursos coesivos.
    """
    rule_5 = """
        A 5a competência cobrada pela correção é: Elaborar proposta de intervenção para o problema abordado, respeitando os direitos humanos. 
        Analisa a capacidade do candidato de propor uma intervenção viável e ética para o problema abordado no texto.

        Nesta competência, o sistema de pontuação é dividido em seis níveis de desempenho, que são:

        - 0:  Não apresenta proposta de intervenção ou apresenta proposta não relacionada ao tema ou ao assunto.
        - 40: Apresenta proposta de intervenção vaga, precária ou relacionada apenas ao assunto.
        - 80: Elabora, de forma insuficiente, proposta de intervenção relacionada ao tema ou não articulada com a discussão desenvolvida no texto.
        - 120: Elabora, de forma mediana, proposta de intervenção relacionada ao tema e articulada à discussão desenvolvida no texto.
        - 160: Elabora bem proposta de intervenção relacionada ao tema e articulada à discussão desenvolvida no texto.
        - 200: Elabora muito bem proposta de intervenção, detalhada, relacionada ao tema e articulada à discussão desenvolvida no texto.
    """
    rule_6 = "Ao dar a pontuação em alguma competência, traga a justificativa para a pontuação dada e traga referências do contexto adicional \n\n{context_query}\n\n."
    rule_7 = "A redação deve ser zerada quando houver: Fuga total ao tema; Estruturação inadequada do texto; Redação inferior a 7 linhas; Desrespeito aos Direitos Humanos."
    rule_8 = "Não seja tão rígido com a correção. Lembre-se que o objetivo é ajudar o usuário a melhorar sua redação."
    rule_9 = "Você irá corrigir a redação com base nessas competências. Pontue cada competência de acordo com o desempenho do usuário. Ao final, a nota final será a soma das pontuações em todas as compentências. Informe a nota final no final da correção."
    # Query
    query = f'''
        Com base nas competências cobradas pela correção do ENEM, corrija a redação do usuário.

        O tema e sua contextualização são: Desafios para o enfrentamento da invisibilidade do trabalho de cuidado realizado pela mulher no Brasil.

        A redação do usuário é: {redacao}.
    '''

    # Messages
    messages = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_1),
        SystemMessage(content=rule_2),
        SystemMessage(content=rule_3),
        SystemMessage(content=rule_4),
        SystemMessage(content=rule_5),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_8),
        SystemMessage(content=rule_9),
        SystemMessage(content=query),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-0125")
    
    chain_out = (
            {
                "context_query": itemgetter("rag_quary") | chain_rag 
            }   
            | prompt
            | llm
            | StrOutputParser()
    )
    
    rag_quary = "Busque documentos relevantes para os critérios de correção do ENEM."
    with st.chat_message("Human", avatar="👤"):
        st.markdown(chain_out.invoke({"query": redacao, "rag_quary": rag_quary}))