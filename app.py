import streamlit as st
import pandas as pd
from google_auth import conectar_planilha
from mapa import exibir_mapa
from formulario import formulario_envio
from info import exibir_informacoes

# ID da planilha (extraído da URL do Google Sheets) e nome da aba
NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
NOME_ABA = "DB_mapa"

def main():
    st.set_page_config(layout="wide")
    st.title("🌿 Plataforma Colaborativa da Araruta como PANC")

    aba = st.sidebar.radio("Navegação", ["🌎 Mapa", "➕ Contribuir", "📚 Informações"])

    try:
        # Conecta à planilha e aba correta
        aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)
        df = df.dropna(subset=["latitude", "longitude"])
    except Exception as e:
        st.error("❌ Erro ao carregar os dados da planilha. Verifique se o ID da planilha e o nome da aba estão corretos, e se a planilha foi compartilhada com a conta de serviço.")
        st.exception(e)
        return

    if aba == "🌎 Mapa":
        st.markdown("Visualize os pontos de cultivo da araruta mapeados colaborativamente:")
        exibir_mapa(df)

    elif aba == "➕ Contribuir":
        formulario_envio(aba_dados)

    elif aba == "📚 Informações":
        exibir_informacoes()

if __name__ == "__main__":
    main()
