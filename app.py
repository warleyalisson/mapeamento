import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

NOME_PLANILHA = "Mapa Araruta - PANC (colaborativo)"

def main():
    st.set_page_config(layout="wide")
    st.title("🌿 Plataforma Colaborativa da Araruta como PANC")

    aba = st.sidebar.radio("Navegação", ["🌎 Mapa", "➕ Contribuir", "📚 Informações"])

    try:
        sheet = conectar_planilha(NOME_PLANILHA)
        registros = sheet.get_all_records()
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
        formulario_envio(sheet)

    elif aba == "📚 Informações":
        exibir_informacoes()

if __name__ == "__main__":
    main()
