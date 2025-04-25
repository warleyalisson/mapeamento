import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

# Nome do arquivo da planilha e da aba interna
NOME_PLANILHA = "Mapa Araruta - PANC (colaborativo)"
NOME_ABA = "DB_mapa"

def main():
    st.set_page_config(layout="wide")
    st.title("🌿 Plataforma Colaborativa da Araruta como PANC")

    aba = st.sidebar.radio("Navegação", ["🌎 Mapa", "➕ Contribuir", "📚 Informações"])

    try:
        # Conectar à aba DB_mapa da planilha
        planilha = conectar_planilha(NOME_PLANILHA)
        aba_dados = planilha.worksheet(NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)
        df = df.dropna(subset=["latitude", "longitude"])
    except Exception as e:
        st.error("Erro ao carregar os dados da planilha.")
        st.exception(e)
        return

    if aba == "🌎 Mapa":
        st.markdown("Visualize os pontos já cadastrados no mapa interativo:")
        exibir_mapa(df)

    elif aba == "➕ Contribuir":
        formulario_envio(aba_dados)

    elif aba == "📚 Informações":
        exibir_informacoes()

if __name__ == "__main__":
    main()
