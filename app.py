import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

# Configurações gerais do app (tema claro/minimalista)
st.set_page_config(
    page_title="🌿 Mapeamento da Araruta",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização adicional para deixar mais bonito
st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 12px;
    }
    .stSidebar {
        background-color: #e6f2e6;
    }
    h1 {
        color: #006400;
    }
    h2 {
        color: #228B22;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🌿 Plataforma Colaborativa: Mapeamento da Araruta como PANC")

    aba = st.sidebar.radio("Navegação 🧭", ["🌎 Ver Mapa", "➕ Adicionar Novo Ponto", "📚 Informações"])

    NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
    NOME_ABA = "Página1"

    try:
        aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)
        df = df.dropna(subset=["latitude", "longitude"])
    except Exception as e:
        st.error("❌ Erro ao carregar dados da planilha.")
        st.exception(e)
        return

    st.markdown("<br>", unsafe_allow_html=True)

    if aba == "🌎 Ver Mapa":
        with st.container():
            st.header("🗺️ Mapa de Cultivos")
            exibir_mapa(df)

    elif aba == "➕ Adicionar Novo Ponto":
        with st.container():
            st.header("📍 Cadastro de Novo Ponto de Cultivo")
            formulario_envio(aba_dados)

    elif aba == "📚 Informações":
        with st.container():
            st.header("📖 Sobre a Araruta como PANC")
            exibir_informacoes()

if __name__ == "__main__":
    main()
