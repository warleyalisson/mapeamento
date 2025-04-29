import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Função para exibir o mapa com os pontos da planilha
def exibir_mapa(sheet):
    st.subheader("🗺️ Mapa de pontos cadastrados")

    try:
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)

        # Verificação mínima
        if df.empty or "latitude" not in df.columns or "longitude" not in df.columns:
            st.warning("⚠️ Nenhum dado com coordenadas encontrado.")
            return

        # Conversão de tipos
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        df = df.dropna(subset=["latitude", "longitude"])

        if df.empty:
            st.warning("⚠️ Nenhuma coordenada válida encontrada.")
            return

        # Mapa centrado no primeiro ponto válido
        lat_center = df["latitude"].mean()
        lon_center = df["longitude"].mean()
        mapa = folium.Map(location=[lat_center, lon_center], zoom_start=5)

        # Adiciona os pontos no mapa
        for _, row in df.iterrows():
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
        st.error("❌ Erro ao carregar os dados da planilha.")
        st.exception(e)
