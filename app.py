import streamlit as st
from google_auth import conectar_planilha
from formulario import formulario_envio
from mapa import exibir_mapa

# Nome da planilha e aba
NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
NOME_ABA = "DB_mapa"

# Configurações iniciais
st.set_page_config(page_title="🌱 Mapeamento Araruta PANC", layout="wide")
st.markdown("<style>html, body, [class*='css'] {font-family: 'Open Sans', sans-serif;}</style>", unsafe_allow_html=True)

# Cabeçalho
st.title("🌿 Plataforma Colaborativa - Araruta como PANC")
st.caption("Conectando produtores e pesquisadores de Araruta de todo o Brasil.")

# Menu lateral
st.sidebar.header("📋 Navegação")
menu = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["Início", "Cadastrar novo ponto", "Visualizar Mapa", "Informações"]
)

# Conexão com a planilha
try:
    aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
except Exception as e:
    aba_dados = None
    st.error("❌ Erro ao conectar à planilha.")
    st.exception(e)

# Corpo principal
st.divider()

if aba_dados:
    if menu == "Início":
        st.subheader("👋 Bem-vindo à Plataforma!")
        st.markdown("""
        Esta plataforma colaborativa permite:
        - 📍 **Cadastrar** locais de cultivo da araruta.
        - 🗺️ **Visualizar** um mapa interativo dos pontos cadastrados.
        - 🔍 **Buscar informações** para fomentar o cultivo como PANC.

        **Use o menu lateral** para navegar.
        """)
    elif menu == "Cadastrar novo ponto":
        st.subheader("📝 Cadastro de novo ponto de cultivo")
        formulario_envio(aba_dados)
    elif menu == "Visualizar Mapa":
        st.subheader("🗺️ Mapa de Cultivos Cadastrados")
        exibir_mapa(aba_dados)
    elif menu == "Informações":
        st.subheader("📚 Informações sobre a Araruta")
        st.markdown("""
        ### 🌿 Sobre a Araruta
        - **Nome científico:** Maranta arundinacea
        - **Utilização:** Fonte de amido altamente digerível.
        - **Cultivo:** Planta rústica, adaptável a diferentes tipos de solo.

        ### 📍 Como encontrar a Araruta
        - Verifique no mapa os locais cadastrados.
        - Utilize as informações de contato em cada marcador.

        ### 📬 Contato Geral
        - **Telefone:** (31) 99999-9999
        - **E-mail:** contato@ararutapanc.org
        - **Instagram:** [@ararutapanc](https://www.instagram.com)

        ### 📖 Saiba mais
        - [Guia Completo de Cultivo da Araruta (PDF)](https://exemplo.com/guia_araruta)
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Dados indisponíveis no momento. Sistema em modo offline.")

# Rodapé
st.divider()
st.markdown(
    "<center><small style='color: gray;'>© 2025 Warley Alisson - Plataforma de Pesquisa e Desenvolvimento</small></center>",
    unsafe_allow_html=True
)
