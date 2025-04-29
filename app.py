import streamlit as st
from google_auth import conectar_planilha
from formulario import formulario_envio
from mapa import exibir_mapa

# Nome da planilha e da aba
NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
NOME_ABA = "DB_mapa"

# Título e configuração da página
st.set_page_config(page_title="Mapeamento da Araruta como PANC", layout="wide")
st.title("🌱 Plataforma Colaborativa - Araruta como PANC")

# Menu de navegação
menu = st.sidebar.selectbox(
    "Menu",
    ["Início", "Cadastrar novo ponto", "Visualizar Mapa", "Informações"]
)

# Conectar à planilha
try:
    aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
except Exception as e:
    aba_dados = None
    st.error("❌ Erro ao conectar à planilha. Verifique se está compartilhada corretamente.")
    st.exception(e)

# Controle de telas
if aba_dados:
    if menu == "Início":
        st.markdown("""
        ### 👋 Bem-vindo à Plataforma de Mapeamento da Araruta 🌿
        Esta plataforma colaborativa permite:
        - 📍 Cadastrar locais de cultivo de araruta (PANC).
        - 🗺️ Visualizar um mapa interativo com os pontos cadastrados.
        - 🔍 Buscar informações para fomentar o cultivo da araruta.

        Selecione uma opção no menu lateral para começar!
        """)
    elif menu == "Cadastrar novo ponto":
        formulario_envio(aba_dados)
    elif menu == "Visualizar Mapa":
        exibir_mapa(aba_dados)
    elif menu == "Informações":
        st.header("📚 Informações sobre a Araruta e Contato")

        st.markdown("""
        ### 📍 Como encontrar a Araruta
        - Verifique no mapa os locais já cadastrados.
        - Utilize as informações de contato fornecidas em cada marcador.

        ### 📬 Contato Geral
        - **Telefone:** (31) 99999-9999
        - **E-mail:** contato@ararutapanc.org
        - **Instagram:** [@ararutapanc](https://www.instagram.com)

        ### 🌱 Sobre a Araruta (Maranta arundinacea)
        - A araruta é uma planta alimentícia não convencional (PANC).
        - Rica em amido de alta digestibilidade.
        - Adaptável a diferentes solos e climas.

        ### 📖 Saiba mais
        - [Guia Completo de Cultivo da Araruta (PDF)](https://exemplo.com/guia_araruta)
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Não foi possível carregar os dados. Sistema em modo offline.")

# Rodapé
st.markdown("---")
st.markdown(
    "<center><small>Desenvolvido por Warley Alisson | Plataforma de Pesquisa 2025</small></center>",
    unsafe_allow_html=True
)
