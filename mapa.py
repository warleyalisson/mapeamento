import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Função para exibir o mapa com os pontos
def exibir_mapa(sheet):
    st.subheader("🗺️ Mapa de pontos cadastrados")

    try:
        # Se for planilha (gspread) ou DataFrame
        if hasattr(sheet, "get_all_records"):
            df = pd.DataFrame(sheet.get_all_records())
        else:
            df = sheet

        if df.empty:
            st.warning("⚠️ Nenhum dado encontrado.")
            return

        # Confere se as colunas necessárias existem
        if "latitude" not in df.columns or "longitude" not in df.columns:
            st.warning("⚠️ Dados de latitude e longitude não encontrados.")
            return

        # Conversão de tipos para segurança
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        df_validos = df.dropna(subset=["latitude", "longitude"])

        # Se houver pontos válidos, centra no meio deles
        if not df_validos.empty:
            lat_center = df_validos["latitude"].mean()
            lon_center = df_validos["longitude"].mean()
            mapa = folium.Map(location=[lat_center, lon_center], zoom_start=5)
        else:
            # Se não houver pontos válidos, centra no Brasil
            st.warning("⚠️ Nenhuma coordenada válida. Mapa centralizado no Brasil.")
            mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

        # Adiciona os marcadores se houver dados
        for _, row in df_validos.iterrows():
            popup_html = f"""
                <b>Endereço:</b> {row.get('endereco_completo', 'Não informado')}<br>
                <b>Relato:</b> {row.get('relato', 'Sem relato')}<br>
                <b>Telefone:</b> {row.get('telefone_contato', 'Não informado')}<br>
                <b>E-mail:</b> {row.get('email_contato', 'Não informado')}
            """
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="green", icon="leaf")
            ).add_to(mapa)

        # Exibir no Streamlit
        st_folium(mapa, width=800, height=600)

    except Exception as e:
        st.error("❌ Erro ao carregar os dados do mapa.")
        st.exception(e)
