import streamlit as st
from streamlit import session_state as ss
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from modules.nav import MenuButtons


CONFIG_FILENAME = 'config.yaml'

with open(CONFIG_FILENAME) as file:
    config = yaml.load(file, Loader=SafeLoader)

# st.header('Login')

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# login_tab = st.tabs(['Login'])
# print('login_tab', login_tab)
# with login_tab:
# authenticator.login(location='main')

if ss["authentication_status"]:
    authenticator.logout(location='sidebar')  
    st.header('Bem-vindo (a) ao EduBot!')  
    # import streamlit as st

    # st.set_page_config(layout="wide")

    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<p class="big-font">Olá {ss["name"]}!</p>\n<p class="big-font">Navegue nas abas laterais!</p>', unsafe_allow_html=True)
    # st.write(f'Bem-vindo (a) *{ss["name"]}*')

elif ss["authentication_status"] is False:
    st.error('Username/senha está errado')
elif ss["authentication_status"] is None:
    st.warning('Por favor insira seu username e senha')

# st.header('Login')
authenticator.login(location='main')

# with register_tab:
#     if not ss["authentication_status"]:
#         try:
#             email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
#             if email_of_registered_user:
#                 st.success('Usuário registrado com sucesso')
#         except Exception as e:
#             st.error(e)



# Call this late because we show the page navigator depending on who logged in.
MenuButtons()
