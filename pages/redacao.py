import streamlit as st
from utils import*

import base64
import mimetypes
import mimetypes
import base64
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




