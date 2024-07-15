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
    
    template = """ \n
    Aqui está o texto de redação: {texto} \n
    Mantenha apenas o texto dividido em paragrafos, retire todas as informações como NOME, IDADE entre outros e mantenha apenas a redação
    Saída (Texto de redação):"""


    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        prompt 
        | ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, model="gpt-4o")
        | StrOutputParser() 
        | {"redacao_limpa": RunnablePassthrough()}
    )

    # Rules
    base_rule = "Você é um corretor de redações do ENEM. Você irá corrigir a redação do usuário, cujo  o tema e sua contextualização são: {tema}, seguindo os critérios de correção do ENEM, existem 5 competências avaliadas."

    rule_1 = """
        A primeira competência avaliada é o domínio da escrita formal da língua portuguesa. 
        Seu objetivo é verificar se a redação está adequada às regras de ortografia, como acentuação, uso de hífen, letras maiúsculas e minúsculas, e separação silábica.
        Você também deve analisar a regência, concordância, pontuação, paralelismo, emprego de pronomes e crase. 
        Não considerar possíveis erros de formatação, como espaços entre os caracteres; focar nos aspectos mencionados acima.

        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Desconhecimento da modalidade escrita formal da Língua Portuguesa.
        características nota 0: O texto apresenta um excesso de desvios gramaticais e de convenções de escrita que tornam a compreensão do texto impossível.

        40: Domínio precário da modalidade escrita formal da Língua Portuguesa, com frequentes desvios gramaticais e de convenções da escrita.
        características nota 40: Neste texto, o participante demonstra domínio insuficiente da norma padrão, evidenciado por graves e frequentes desvios gramaticais e de convenções da escrita, além da presença de gírias e marcas de oralidade. Esta pontuação é atribuída a participantes que apresentam muitos desvios gravíssimos de forma sistemática, acompanhados por excessiva desestruturação sintática.

        80: Domínio insuficiente da modalidade escrita formal da Língua, com muitos desvios gramaticais e de convenções da escrita.
        características nota 80: O texto apresenta uma grande quantidade de desvios gramaticais e de convenções da escrita graves ou gravíssimos, além de marcas de oralidade, como a falta de concordância do verbo com o sujeito (com sujeito depois do verbo ou muito distante dele), falta de concordância do adjetivo com o substantivo, regência nominal e verbal inadequada (ausência ou emprego indevido de preposição), ausência do acento indicativo da crase ou seu uso inadequado, problemas na estrutura sintática como frases justapostas sem conectivos ou orações subordinadas sem oração principal, desvios em palavras de grafia complexa, separação incorreta de sujeito, verbo, objeto direto e indireto por vírgula, e marcas de oralidade. Além disso, podem ser observados períodos incompletos ou truncados que comprometem a compreensão, graves problemas de pontuação, desvios graves de grafia e acentuação, como letra minúscula no início de frases e nomes próprios, e a presença de gíria.

        120: Domínio mediano da modalidade escrita formal da Língua Portuguesa, com alguns desvios gramaticais e de convenções da escrita.
        características nota 120: O texto pode conter alguns desvios graves de gramática e convenções da escrita, como a falta de concordância do verbo com o sujeito (com sujeito depois do verbo ou muito distante dele), falta de concordância do adjetivo com o substantivo, regência nominal e verbal inadequada (ausência ou emprego indevido de preposição), ausência do acento indicativo da crase ou seu uso inadequado, problemas na estrutura sintática como frases justapostas sem conectivos ou orações subordinadas sem oração principal, desvios em palavras de grafia complexa, separação incorreta de sujeito, verbo, objeto direto e indireto por vírgula, e marcas de oralidade.

        160: Bom domínio da modalidade escrita formal da Língua Portuguesa, com poucos desvios gramaticais e de convenções da escrita.
        características nota 160: O texto pode conter alguns desvios leves de gramática e convenções de escrita, como a ausência de concordância em passiva sintética (por exemplo: uso de "vende-se casas" em vez de "vendem-se casas"), desvios de pontuação que não comprometem o sentido do texto, e erros de ortografia e acentuação que não afetam o entendimento. Desvios mais graves, como a falta de concordância verbal ou nominal, não impedem que a redação receba essa pontuação, desde que não se repitam frequentemente ao longo do texto.

        200: Excelente domínio da modalidade escrita formal da Língua Portuguesa. Desvios gramaticais ou de convenções da escrita são aceitos apenas como exceção e se não houver reincidência.
        características nota 200: O texto deve mostrar ausência de características de oralidade e registro informal, precisão vocabular e conformidade com as regras gramaticais. Deve ter poucos ou nenhum desvio leve de gramática ou convenções da escrita. Erros mais graves, como falta de concordância verbal, impedem a obtenção da pontuação mais alta.

    """

    rule_2 =  """
        A segunda competência avaliada é a compreensão da proposta de redação e a aplicação de conceitos de várias áreas do conhecimento para desenvolver o tema dentro dos limites do texto dissertativo-argumentativo em prosa. 
        Seu objetivo é verificar se o candidato compreendeu a proposta de redação e conseguiu desenvolver um texto dissertativo-argumentativo utilizando conhecimentos de diferentes áreas.
        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Fuga ao tema ou não atendimento à estrutura dissertativo-argumentativa.
        características nota 0: O participante desenvolve um texto que não atende à proposta de redação, abordando outro tema ou utilizando uma estrutura textual diferente da dissertativo-argumentativa. Por exemplo, pode criar um poema, descrever algo ou contar uma história, em vez de argumentar conforme solicitado.
        
        40: Apresenta o assunto tangenciando o tema ou demonstra domínio precário do texto dissertativo-argumentativo, com traços constantes de outros tipos textuais.
        características nota 40: O desenvolvimento tangencial do tema revela uma má interpretação do tema proposto, focando em um assunto vinculado, mas não central ao tema. Apresenta inadequação ao tipo textual dissertativo-argumentativo, com repetição de ideias e ausência de argumentação coerente. Pode ainda ocorrer a elaboração de um texto mais narrativo, com apenas um resquício dissertativo, como contar uma história longa e afirmar no final que ela confirma uma determinada tese.
        
        80: Desenvolve o tema recorrendo à cópia dos textos motivadores ou apresenta domínio insuficiente do texto dissertativo-argumentativo, sem atender à estrutura com proposição, argumentação e conclusão.
        características nota 80:O participante desenvolve o tema de forma mediana, com uma tendência ao tangenciamento. Apresenta uma argumentação previsível, baseada em argumentos do senso comum ou cópias dos textos motivadores. Demonstrando um domínio precário do tipo textual dissertativo-argumentativo, a argumentação pode ser falha ou o texto pode se limitar apenas à dissertação sem uma estrutura argumentativa clara.
        
        120: Desenvolve o tema por meio de argumentação previsível e apresenta domínio mediano do texto dissertativo-argumentativo, com proposição, argumentação e conclusão.
        características nota 120: Desenvolve de forma adequada o tema, porém apresenta uma abordagem superficial ao discutir outras questões relacionadas. Apresenta uma argumentação previsível e demonstra domínio adequado do tipo textual dissertativo-argumentativo, mas não explicita claramente uma tese, focando mais no caráter dissertativo do que no argumentativo. Além disso, reproduz ideias do senso comum no desenvolvimento do tema.
        
        160: Desenvolve o tema por meio de argumentação consistente e apresenta bom domínio do texto dissertativo-argumentativo, com proposição, argumentação e conclusão.
        características nota 160:O participante desenvolve o tema de forma satisfatória, porém sem explorar plenamente seus aspectos principais. Apresenta uma argumentação consistente e demonstra bom domínio do tipo textual dissertativo-argumentativo, mas os argumentos não são bem desenvolvidos. Eles não se limitam à reprodução das ideias dos textos motivadores nem se restringem a questões do senso comum.
        
        200: Desenvolve o tema por meio de argumentação consistente, a partir de um repertório sociocultural produtivo, e apresenta excelente domínio do texto dissertativo-argumentativo.
        características nota 200:Tema muito bem desenvolvido, explorando seus principais aspectos. O texto está estruturado com uma introdução clara, onde a tese é explicitada; os argumentos são apresentados de forma distribuída em diferentes parágrafos para comprovar a tese; e há um parágrafo final que propõe uma intervenção, funcionando como conclusão. Os argumentos não se limitam à reprodução das ideias dos textos motivadores nem se restringem a questões do senso comum.
    """

    rule_3 = """
        A terceira competência avaliada é a capacidade de selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista. 
        Seu objetivo é verificar a habilidade do candidato em fazer isso de forma coerente e coesa.

        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Apresenta informações, fatos e opiniões que não estão relacionados ao tema proposto e não defendem um ponto de vista específico.
        características nota 0: Informações, fatos, opiniões e argumentos incoerentes enão apresenta um ponto de vista.

        40: Apresenta informações, fatos e opiniões pouco relacionados ao tema ou incoerentes, sem defender claramente um ponto de vista.
        características nota 40: Não há defesa de ponto de vista, não apresentando opinião sobre o tema proposto. As informações, fatos, opiniões e argumentos são pouco relacionados ao tema e entre si, resultando em uma articulação incoerente.

        80: Apresenta informações, fatos e opiniões relacionados ao tema, porém de forma desorganizada ou contraditória, e limitados aos argumentos dos textos motivadores, sem uma defesa clara e independente de um ponto de vista.
        características nota 80: Apresenta informações, fatos e opiniões pouco articulados ou contraditórios, embora pertinentes ao tema proposto. O texto se limita a reproduzir os argumentos constantes na proposta de redação, em defesa de um ponto de vista.

        120: Apresenta informações, fatos e opiniões relacionados ao tema, mas estão principalmente limitados aos argumentos dos textos motivadores. A organização dessas informações é limitada, e a defesa de um ponto de vista não é completamente clara ou independente.
        características nota 120: Apresenta informações, fatos, opiniões e argumentos pertinentes ao tema proposto, mas os organiza e relaciona de forma pouco consistente em defesa de seu ponto de vista. As informações são aleatórias e desconectadas entre si, embora relacionadas ao tema. O texto revela pouca articulação entre os argumentos, que não são convincentes para defender a opinião do autor.

        160: Apresenta informações, fatos e opiniões relacionados ao tema de forma organizada, demonstrando indícios de autoria ao desenvolver uma defesa clara de um ponto de vista.
        características nota 160: Seleciona, organiza e relaciona informações, fatos, opiniões e argumentos pertinentes ao tema proposto de forma consistente, em defesa de seu ponto de vista. Explicita a tese, seleciona argumentos que possam comprová-la e elabora conclusão ou proposta que mantenha coerência com a opinião defendida na redação. Os argumentos utilizados são previsíveis; entretanto, não há cópia de argumentos dos textos motivadores.

        200: Apresenta informações, fatos e opiniões de forma consistente e organizada, demonstrando autoria na defesa de um ponto de vista relacionado ao tema proposto.
        características nota 200: Seleciona, organiza e relaciona informações, fatos, opiniões e argumentos pertinentes ao tema proposto de forma consistente, configurando autoria, em defesa de seu ponto de vista. Explicita a tese, seleciona argumentos que possam comprová-la e elabora conclusão ou proposta que mantenha coerência com a opinião defendida na redação.

        """
    
    rule_4 = """
        A quarta competência avaliada é o conhecimento dos mecanismos linguísticos necessários para a construção da argumentação. 
        Seu objetivo é verificar o uso adequado de recursos linguísticos, como operadores argumentativos, modalizadores e conectivos, para construir a argumentação.
        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Ausência de marcas de articulação, resultando em fragmentação das ideias.
        características nota 0: Informações desconexas, que não se configuram como texto.
        
        40: Articula as partes do texto de forma precária.
        características nota 40: O participante não articula as partes do texto ou as articula de forma precária e/ou inadequada, apresentando graves e frequentes desvios de coesão textual. Há sérios problemas na articulação das ideias e na utilização de recursos coesivos, como frases fragmentadas, frases sem oração principal, períodos muito longos sem o emprego dos conectores adequados, repetição desnecessária de palavras, e a não utilização de elementos que se refiram a termos que apareceram anteriormente no texto.
        
        80: Articula as partes do texto de forma insuficiente, com muitas inadequações e repertório limitado de recursos coesivos.
        características nota 80: O texto apresenta muitas inadequações na utilização dos recursos coesivos. A redação neste nível pode conter vários desvios, como frases fragmentadas que comprometam a estrutura lógico-gramatical, sequência justaposta de ideias sem encaixamentos sintáticos, ausência de paragrafação, e frases com apenas oração subordinada, sem oração principal. Esta pontuação deve ser atribuída ao participante que demonstrar pouco domínio dos recursos coesivos.
        
        120: Articula as partes do texto de forma mediana, com inadequações e repertório pouco diversificado de recursos coesivos.
        características nota 120: O texto apresenta algumas inadequações na utilização dos recursos coesivos. Além de desvios de menor gravidade, poderá conter eventuais desvios, como frases fragmentadas que comprometam a estrutura lógico-gramatical, sequência justaposta de ideias sem encaixamentos sintáticos, ausência de paragrafação, e frases com apenas oração subordinada, sem oração principal. Esta pontuação deve ser atribuída ao participante que demonstrar domínio regular dos recursos coesivos.

        160: Articula as partes do texto com poucas inadequações e repertório diversificado de recursos coesivos.
        características nota 160: O texto articula bem as partes, com poucas inadequações na utilização de recursos coesivos. Poderá conter alguns desvios de menor gravidade, como emprego equivocado do conector, emprego do pronome relativo sem a preposição, quando obrigatória, repetição desnecessária de palavras ou substituição inadequada sem se valer dos recursos de substituição oferecidos pela língua. Esta pontuação deve ser atribuída ao participante que demonstrar domínio dos recursos coesivos.

        200: Articula bem as partes do texto e apresenta repertório diversificado de recursos coesivos.
        características nota 200:O texto articula muito bem as partes, sem inadequações na utilização dos recursos coesivos. Essa pontuação deve ser atribuída ao participante que demonstrar pleno domínio dos recursos coesivos.
        
    """
    rule_5 = """
        A quinta competência avaliada é a elaboração de uma proposta de intervenção para o problema abordado, respeitando os direitos humanos. 
        Seu objetivo é analisar a capacidade do candidato de propor uma intervenção viável e ética para o problema discutido no texto.
        O sistema de pontuação desta competência é dividido em seis níveis:

        0: Não apresenta proposta de intervenção ou apresenta proposta não relacionada ao tema ou assunto.
        40: Apresenta proposta de intervenção vaga, precária ou relacionada apenas ao assunto.
        80: Elabora de forma insuficiente uma proposta de intervenção relacionada ao tema ou não articulada com a discussão do texto.
        120: Elabora de forma mediana uma proposta de intervenção relacionada ao tema e articulada à discussão do texto.
        160: Elabora bem uma proposta de intervenção relacionada ao tema e articulada à discussão do texto.
        200: Elabora muito bem uma proposta de intervenção detalhada, relacionada ao tema e articulada à discussão do texto.
    """
    rule_6 = "Ao dar a pontuação em alguma competência, traga a justificativa para a pontuação dada usando as características de cada nota, TRAZENDO EXEMPLOS E ALTERNATIVAS DE MELHORIAS PARA O ALUNO. "
    rule_7 = "Dentro dos exemplos, FAÇA UMA JUSTIFICATIVA APROFUNDADA deixando claro como o usuário pode melhorar na prática"
    rule_8 = "A redação deve ser zerada quando houver: Fuga total ao tema; Estruturação inadequada do texto; Redação inferior a 7 linhas; Desrespeito aos Direitos Humanos."
    rule_9 = "Não seja tão rígido com a correção. Lembre-se que o objetivo é ajudar o usuário a melhorar sua redação."
    rule_10 = "Você irá corrigir a redação com base nessas competências e suas características. Pontue cada competência de acordo com o desempenho do usuário EVITE COMENTÁRIOS QUE FOQUEM NA FORMATAÇÃO DA ESCRITA DO USUÁRIO, FOQUE NO CONTEÚDO. Escreva no topo da correção EXATAMENTE o tema da redação que lhe foi passado"
    comp_template = """Escreva sua resposta no formato usando markdown:
    ## Competência 1 - Nota: (nota)
    (lista de justificativas e sugestões de melhoria) - use listas com markdown
    """
    combined_rules = """Repita as entradas de cada competência, mantendo o formato original na estrutura, substitua a nota_total pela soma das notas das competências, substitua o tema_redacao pelo tema da redação:
    ## Tema da redação: (tema_redacao)
    # Nota total: (nota_total)
    {competencia_1}
    {competencia_2}
    {competencia_3}
    {competencia_4}
    {competencia_5}

    """

    prompt_combined = ChatPromptTemplate.from_template(combined_rules)

        
    llm = ChatOpenAI(temperature=0, model="gpt-4o")

    messages_comp1 = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_1),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_9),
        SystemMessage(content=rule_10),
        SystemMessage(content=comp_template),
        ('system', "Dê a pontuação da competência 1 e traga a justificativa para a pontuação dada. A redação do usuário é: {redacao_limpa}.")
    ]

    messages_comp2 = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_2),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_9),
        SystemMessage(content=rule_10),
        SystemMessage(content=comp_template),
        ('system', "Dê a pontuação da competência 2 e traga a justificativa para a pontuação dada. A redação do usuário é: {redacao_limpa}.")
    ]

    messages_comp3 = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_3),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_9),
        SystemMessage(content=rule_10),
        SystemMessage(content=comp_template),
        ('system', "Dê a pontuação da competência 3 e traga a justificativa para a pontuação dada. A redação do usuário é: {redacao_limpa}.")
    ]

    messages_comp4 = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_4),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_9),
        SystemMessage(content=rule_10),
        SystemMessage(content=comp_template),
        ('system', "Dê a pontuação da competência 4 e traga a justificativa para a pontuação dada. A redação do usuário é: {redacao_limpa}.")
    ]

    messages_comp5 = [
        SystemMessage(content=base_rule),
        SystemMessage(content=rule_5),
        SystemMessage(content=rule_6),
        SystemMessage(content=rule_7),
        SystemMessage(content=rule_9),
        SystemMessage(content=rule_10),
        SystemMessage(content=comp_template),
        ('system', "Dê a pontuação da competência 5 e traga a justificativa para a pontuação dada. A redação do usuário é: {redacao_limpa}.")
    ]

    prompt_comp1 = ChatPromptTemplate.from_messages(messages_comp1)
    prompt_comp2 = ChatPromptTemplate.from_messages(messages_comp2)
    prompt_comp3 = ChatPromptTemplate.from_messages(messages_comp3)
    prompt_comp4 = ChatPromptTemplate.from_messages(messages_comp4)
    prompt_comp5 = ChatPromptTemplate.from_messages(messages_comp5)

    chain_comp1 = (
        prompt_comp1
        | llm
        | StrOutputParser()
    )

    chain_comp2 = (
        prompt_comp2
        | llm
        | StrOutputParser()
    )

    chain_comp3 = (
        prompt_comp3
        | llm
        | StrOutputParser()
    )

    chain_comp4 = (
        prompt_comp4
        | llm
        | StrOutputParser()
    )

    chain_comp5 = (
        prompt_comp5
        | llm
        | StrOutputParser()
    )

    chain_correcao = (
                chain
                | {
                    "competencia_1": chain_comp1,
                    "competencia_2": chain_comp2,
                    "competencia_3": chain_comp3,
                    "competencia_4": chain_comp4,
                    "competencia_5": chain_comp5
                }
                | prompt_combined
                | llm
                | StrOutputParser()
    )
    
    return st.markdown(chain_correcao.invoke({'texto' : texto,  "tema" : tema}))

button_correcao = st.button("Corrigir", type="primary")
if button_correcao:
    with st.chat_message("Human", avatar="👤"):
        corrige(uploaded_file, tema)

from openai import OpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def image_to_base64(image_path):
    # Adivinha o tipo MIME da imagem
    mime_type, _ = mimetypes.guess_type(image_path)
    
    # Verifica se o tipo MIME é válido e se é uma imagem
    if not mime_type or not mime_type.startswith('image'):
        raise ValueError("The file type is not recognized as an image")
    
    # Lê os dados binários da imagem
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Formata o resultado com o prefixo apropriado
    image_base64 = f"data:{mime_type};base64,{encoded_string}"
    
    return image_base64


client = OpenAI(api_key= OPENAI_API_KEY)

def transcribe_image(image_path):
    base64_string = image_to_base64(image_path)
    # Make an API call to submit the image for transcription
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcreva essa redação EXATAMENTE como ela está manuscrita, sem realizar NENHUMA troca de palavras ou elementos coesivos"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_string,
                        "detail": "high"
                    }
                },
            ],
        }
    ],
    max_tokens=4096,
)

    return response.choices[0].message.content

st.title("Corretor de Redação - Envie ao EduBot")
st.subheader("Redação")

uploaded_file = st.file_uploader("Escolha um arquivo")

button_correcao = st.button("Corrigir", type="primary")
if button_correcao:
    # Caminho da imagem
    image_path = 'imgs/redacao.jpg'

    # Converte a imagem para base64
    image_base64 = transcribe_image(image_path)

    # Exibe a string base64 usando st.write
    st.write(image_base64)



