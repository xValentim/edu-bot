import streamlit as st
from utils import*

import base64
import mimetypes
import mimetypes
import base64
from io import StringIO
from openai import OpenAI
from PyPDF2 import PdfReader

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


st.title("Corretor de Redação - Envie ao EduBot")
cs_sidebar()

uploaded_file = st.file_uploader("Upload a file", type=['pdf'])
tema = st.chat_input("Insira o tema da redação")

def corrige(uploaded_file, tema):
    doc = PdfReader(uploaded_file)

    texto = [doc.pages[i].extract_text() for i in range(len(doc.pages))]

    st.session_state.retriever = st.session_state.db.as_retriever(search_kwargs={"k": 10})

    chain_rag = st.session_state.retriever | format_docs
    
    template = """ \n
    Aqui está o texto de redação: {texto} \n
    Mantenha apenas o texto dividido em paragrafos, retire todas as informações como NOME, IDADE entre outros e mantenha apenas a redação
    Saída (Texto de redação):"""


    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        prompt 
        | ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-0125")
        | StrOutputParser() 
    )

    # Rules
    base_rule = "Você é um corretor de redações do ENEM. Você irá corrigir a redação do usuário seguindo os critérios de correção do ENEM. O tema e sua contextualização são: {tema}"

    rule_1 = """
    A primeira competência avaliada é o domínio da escrita formal da língua portuguesa. 
    Ela verifica se a redação está adequada às regras de ortografia, como acentuação, uso de hífen, letras maiúsculas e minúsculas, e separação silábica. 
    Também são analisadas a regência, concordância, pontuação, paralelismo, emprego de pronomes e crase.

    O sistema de pontuação desta competência é dividido em seis níveis:

    0: Desconhecimento da modalidade escrita formal da Língua Portuguesa.
    40: Domínio precário da modalidade escrita formal da Língua Portuguesa, com frequentes desvios gramaticais e de convenções da escrita.
    80: Domínio insuficiente da modalidade escrita formal da Língua, com muitos desvios gramaticais e de convenções da escrita.
    120: Domínio mediano da modalidade escrita formal da Língua Portuguesa, com alguns desvios gramaticais e de convenções da escrita.
    160: Bom domínio da modalidade escrita formal da Língua Portuguesa, com poucos desvios gramaticais e de convenções da escrita.
    200: Excelente domínio da modalidade escrita formal da Língua Portuguesa. Desvios gramaticais ou de convenções da escrita são aceitos apenas como exceção e se não houver reincidência.
    """

    rule_2 =  """
    A segunda competência avaliada é a compreensão da proposta de redação e a aplicação de conceitos de várias áreas do conhecimento para desenvolver o tema dentro dos limites do texto dissertativo-argumentativo em prosa. 
    Ela verifica se o candidato compreendeu a proposta de redação e conseguiu desenvolver um texto dissertativo-argumentativo utilizando conhecimentos de diferentes áreas.
    O sistema de pontuação desta competência é dividido em seis níveis:

    0: Fuga ao tema ou não atendimento à estrutura dissertativo-argumentativa.
    40: Apresenta o assunto tangenciando o tema ou demonstra domínio precário do texto dissertativo-argumentativo, com traços constantes de outros tipos textuais.
    80: Desenvolve o tema recorrendo à cópia dos textos motivadores ou apresenta domínio insuficiente do texto dissertativo-argumentativo, sem atender à estrutura com proposição, argumentação e conclusão.
    120: Desenvolve o tema por meio de argumentação previsível e apresenta domínio mediano do texto dissertativo-argumentativo, com proposição, argumentação e conclusão.
    160: Desenvolve o tema por meio de argumentação consistente e apresenta bom domínio do texto dissertativo-argumentativo, com proposição, argumentação e conclusão.
    200: Desenvolve o tema por meio de argumentação consistente, a partir de um repertório sociocultural produtivo, e apresenta excelente domínio do texto dissertativo-argumentativo.
    """

    rule_3 = """
        A terceira competência avaliada é a capacidade de selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista. 
        Ela verifica a habilidade do candidato em fazer isso de forma coerente e coesa.

        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Ausência de marcas de articulação, resultando em fragmentação das ideias.
        40: Articula as partes do texto de forma precária.
        80: Articula as partes do texto de forma insuficiente, com muitas inadequações e repertório limitado de recursos coesivos.
        120: Articula as partes do texto de forma mediana, com inadequações e repertório pouco diversificado de recursos coesivos.
        160: Articula as partes do texto com poucas inadequações e repertório diversificado de recursos coesivos.
        200: Articula bem as partes do texto e apresenta repertório diversificado de recursos coesivos.
        """
    
    rule_4 = """
        A quarta competência avaliada é o conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. Ela verifica o uso adequado de recursos linguísticos, como operadores argumentativos, modalizadores e conectivos, para construir a argumentação.

        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Ausência de marcas de articulação, resultando em fragmentação das ideias.
        40: Articula as partes do texto de forma precária.
        80: Articula as partes do texto de forma insuficiente, com muitas inadequações e repertório limitado de recursos coesivos.
        120: Articula as partes do texto de forma mediana, com inadequações e repertório pouco diversificado de recursos coesivos.
        160: Articula as partes do texto com poucas inadequações e repertório diversificado de recursos coesivos.
        200: Articula bem as partes do texto e apresenta repertório diversificado de recursos coesivos.
    """
    rule_5 = """
        A quinta competência avaliada é a elaboração de uma proposta de intervenção para o problema abordado, respeitando os direitos humanos.
        Ela analisa a capacidade do candidato de propor uma intervenção viável e ética para o problema discutido no texto.
        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Não apresenta proposta de intervenção ou apresenta proposta não relacionada ao tema ou assunto.
        40: Apresenta proposta de intervenção vaga, precária ou relacionada apenas ao assunto.
        80: Elabora de forma insuficiente uma proposta de intervenção relacionada ao tema ou não articulada com a discussão do texto.
        120: Elabora de forma mediana uma proposta de intervenção relacionada ao tema e articulada à discussão do texto.
        160: Elabora bem uma proposta de intervenção relacionada ao tema e articulada à discussão do texto.
        200: Elabora muito bem uma proposta de intervenção detalhada, relacionada ao tema e articulada à discussão do texto.
    """

    rule_6 = "Ao dar a pontuação em alguma competência, traga a justificativa para a pontuação dada, trazendo exemplos e maneiras de como melhorar nesse critério. Dentro dos exemplos, deixe claro como pode ser feito na prática usando como base esse contexto : \n\n{context_query}\n\n. Sempre que possível, FORNEÇA LINKS dos vídeos relacionados para ajudar o aprendizado do aluno, JAMAIS USE LINKS QUE NÂO FORAM FORNECIDOS A VOCÊ e que NAO EXISTEM."
    rule_7 = "A redação deve ser zerada quando houver: Fuga total ao tema; Estruturação inadequada do texto; Redação inferior a 7 linhas; Desrespeito aos Direitos Humanos."
    rule_8 = "Não seja tão rígido com a correção. Lembre-se que o objetivo é ajudar o usuário a melhorar sua redação."
    rule_9 = "Você irá corrigir a redação com base nessas competências. Pontue cada competência de acordo com o desempenho do usuário EVITE COMENTÁRIOS QUE FOQUEM NA FORMATAÇÃO DA ESCRITA DO USUÁRIO, FOQUE NO CONTEÚDO. Ao final, a nota final será a soma das pontuações em todas as compentências. Informe a nota final no final da correção."

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
        ('system', "Com base nas competências cobradas pela correção do ENEM, corrija a redação do usuário.A redação do usuário é: {redacao}. Escreva no topo da correção exatamente o tema da redação")
    ]

    prompt2 = ChatPromptTemplate.from_messages(messages)

        
    llm = ChatOpenAI(temperature=0.1, model="gpt-4o")

    chain_correcao = (
                {
                    "tema": itemgetter("tema"),
                    "redacao" : chain,
                    "context_query": itemgetter("rag_quary") | chain_rag 
                }
                | prompt2
                | llm
                | StrOutputParser()
            )
    
    rag_quary = "Busque documentos relevantes para os critérios de correção do ENEM."
    
    return st.markdown(chain_correcao.invoke({"texto": texto, "rag_quary": rag_quary, "tema" : tema}))


button_correcao = st.button("Corrigir", type="primary")
if button_correcao:
    with st.chat_message("Human", avatar="👤"):
        corrige(uploaded_file, tema)
        



