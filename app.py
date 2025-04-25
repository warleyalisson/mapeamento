import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

# Nome exato da planilha e da aba conforme o Google Sheets
NOME_PLANILHA = "Mapa Araruta - PANC (colaborativo)"
NOME_ABA = "DB_mapa"

def main():
    st.set_page_config(layout="wide")
    st.title("🌿 Plataforma Colaborativa da Araruta como PANC")

    # Menu lateral de navegação
    aba = st.sidebar.radio("Navegação", ["🌎 Mapa", "➕ Contribuir", "📚 Informações"])

    try:
        # Conectar à planilha e aba corretas
        aba_dados = conectar_planilha(NOME_PLANILHA, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)
        df = df.dropna(subset=["latitude", "longitude"])
    except Exception as e:
        st.error("❌ Erro ao carregar os dados da planilha. Verifique se o nome da planilha e da aba estão corretos e se ela está compartilhada com a conta de serviço.")
        st.exception(e)
        return

    # Módulos por aba
    if aba == "🌎 Mapa":
        st.markdown("Visualize os pontos de cultivo da araruta mapeados colaborativamente:")
        exibir_mapa(df)

    elif aba == "➕ Contribuir":
        st.markdown("Contribua com novos pontos de cultivo da araruta.")
        formulario_envio(aba_dados)

    elif aba == "📚 Informações":
        exibir_informacoes()

if __name__ == "__main__":
    main()
