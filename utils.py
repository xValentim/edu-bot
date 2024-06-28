import base64
import streamlit as st
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pathlib import Path
from langchain_pinecone import PineconeVectorStore

from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from langchain.load import dumps, loads

from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

import yaml

from dotenv import load_dotenv

load_dotenv()

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def cs_sidebar():

    # st.sidebar.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=128 height=128>](https://www.upload.ventures/)'''.format(img_to_bytes("imgs/upload_logo.jpg")), unsafe_allow_html=True)
    st.sidebar.markdown('''[<img src='data:image/png;base64,{}' class='img-fluid' width=112 height=20>](https://neroai.com.br/)'''.format(img_to_bytes("imgs/neroai_logo.png")), unsafe_allow_html=True)
    st.sidebar.markdown(f'Bem-vindo *{st.session_state["name"]}*!')
    st.sidebar.header('Powered by [Nero.AI](https://neroai.com.br/)')

    return None


def vector_db():
    index_name = os.getenv("PINECONE_INDEX_NAME")
    embeddings_size = 1536
    embeddings_model = 'text-embedding-ada-002'
    embeddings = OpenAIEmbeddings(model=embeddings_model)
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    return vectorstore


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Funções auxiliares
def get_strings_from_documents(documents):
    return [doc.page_content for doc in documents]

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def reciprocal_rank_fusion(results: list[list], k=60):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    
    # Initialize a dictionary to hold fused scores for each unique document
    fused_scores = {}

    # Iterate through each list of ranked documents
    for docs in results:
        # Iterate through each document in the list, with its rank (position in the list)
        for rank, doc in enumerate(docs):
            # Convert the document to a string format to use as a key (assumes documents can be serialized to JSON)
            doc_str = dumps(doc)
            # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            # Retrieve the current score of the document, if any
            previous_score = fused_scores[doc_str]
            # Update the score of the document using the RRF formula: 1 / (rank + k)
            fused_scores[doc_str] += 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Return the reranked results as a list of tuples, each containing the document and its fused score
    return reranked_results


def respond(user_query, chat_history, db, retriever):


    template = """Você é um assistente de modelo de linguagem de IA. Sua tarefa é gerar quatro versões diferentes da pergunta fornecida pelo usuário para recuperar 
    documentos relevantes de um banco de dados vetorial. Ao gerar várias perspectivas sobre a pergunta do usuário de contexto semântico idêntico, 
    seu objetivo é ajudar o usuário a superar algumas das limitações da busca de similaridade baseada em distância. 
    Forneça essas perguntas alternativas separadas por novas linhas. \n
    Gere novas perguntas relacionadas a: {user_query} \n
    Saída (4 consultas):"""


    prompt_rag_fusion = ChatPromptTemplate.from_template(template)

    generate_queries = (
        prompt_rag_fusion 
        | ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY, model="gpt-4o")
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )

    #Chain com RRF
    retrieval_chain_rag_fusion = generate_queries | retriever.map() | reciprocal_rank_fusion

    
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
        ('system', "{user_query}"),
    ]
    
    prompt = ChatPromptTemplate.from_messages(all_messages)

    
    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-0125")
    
    chain = (
            {
                "context_query": retrieval_chain_rag_fusion,
                
                "user_query": itemgetter("user_query")
             }
            | prompt
            | llm
            | StrOutputParser()
        )
    
    return chain.stream({"user_query": user_query})

embedding_size = 1536
embedding_model = 'text-embedding-ada-002'
embeddings = OpenAIEmbeddings(model=embedding_model)


# Carrega o arquivo config
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)
    

# import os
# from openai import OpenAI
# import base64
# import mimetypes

# client = OpenAI(api_key='apikey')
# import mimetypes
# import base64

# def image_to_base64(image_path):
#     # Adivinha o tipo MIME da imagem
#     mime_type, _ = mimetypes.guess_type(image_path)
    
#     # Verifica se o tipo MIME é válido e se é uma imagem
#     if not mime_type or not mime_type.startswith('image'):
#         raise ValueError("The file type is not recognized as an image")
    
#     # Lê os dados binários da imagem
#     with open(image_path, 'rb') as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
#     # Formata o resultado com o prefixo apropriado
#     image_base64 = f"data:{mime_type};base64,{encoded_string}"
    
#     return image_base64


# def transcribe_image(image_path):

#     base64_string = image_to_base64(image_path)
#     # Make an API call to submit the image for transcription
#     response = client.chat.completions.create(
#     model="gpt-4-vision-preview",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "Manually transcribe this handwriting"},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": base64_string,
#                         "detail": "low"
#                     }
#                 },
#             ],
#         }
#     ],
#     max_tokens=300,
# )

#     # Print the transcription result
#     print(response)

# # Example usage
# image_path = 'testimage.png'
# transcribe_image('imgs/redacao.jpg')

