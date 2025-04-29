import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

# Configurações gerais do app (visual geral)
st.set_page_config(
    page_title="🌿 Mapeamento da Araruta",
    page_icon="🌱",
    layout="wide",  # Tela larga, igual site moderno
    initial_sidebar_state="expanded"
)

# Estilo customizado para harmonizar com o site oficial
st.markdown("""
<style>
    /* Fundo principal */
    .main {
        background-color: #f8f9fa;
    }
    /* Fundo da sidebar */
    .stSidebar {
        background-color: #e6f2e6;
    }
    /* Títulos em verde escuro */
    h1, h2, h3 {
        color: #006400;
    }
    /* Estilizar botões padrão do Streamlit */
    button[kind="primary"] {
        background-color: #228B22 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
    }
    /* Inputs (caixas de texto) arredondados */
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Definições da Planilha Google
NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
NOME_ABA = "Página1"

def main():
    # Título principal
    st.title("🌿 Plataforma Colaborativa: Mapeamento da Araruta como PANC")

    # Menu lateral de navegação
    aba = st.sidebar.radio("Navegue pelo sistema 🧭", [
        "🌎 Ver Mapa",
        "➕ Adicionar Novo Ponto",
        "📚 Informações"
    ])

    # Tenta carregar os dados da planilha
    try:
        aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)
        df = df.dropna(subset=["latitude", "longitude"])
    except Exception as e:
        st.error("❌ Erro ao carregar dados da planilha.")
        st.exception(e)
        return

    # Adiciona um pequeno espaço entre o título e o conteúdo
    st.markdown("<br>", unsafe_allow_html=True)

    # Redireciona para as páginas
    if aba == "🌎 Ver Mapa":
        with st.container():
            st.header("🗺️ Mapa de Cultivos Cadastrados")
            exibir_mapa(df)

    elif aba == "➕ Adicionar Novo Ponto":
        with st.container():
            st.header("📍 Cadastro de Novo Ponto")
            formulario_envio(aba_dados)

    elif aba == "📚 Informações":
        with st.container():
            st.header("📖 Informações sobre a Araruta e Contatos")
            exibir_informacoes()

if __name__ == "__main__":
    main()
