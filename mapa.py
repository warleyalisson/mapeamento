import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Função para exibir o mapa com correções automáticas
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

        # Checagem de colunas obrigatórias
        colunas_necessarias = ["latitude", "longitude", "endereco_completo", "relato", "telefone_contato", "email_contato"]
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                st.warning(f"⚠️ Coluna '{coluna}' não encontrada.")
                return

        # Corrigir latitudes e longitudes (substituir vírgulas por pontos)
        df["latitude"] = df["latitude"].astype(str).str.replace(",", ".")
        df["longitude"] = df["longitude"].astype(str).str.replace(",", ".")

        # Converter para float
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        # Remover entradas fora do intervalo geográfico normal
        df_validos = df[
            df["latitude"].between(-90, 90) & 
            df["longitude"].between(-180, 180)
        ].dropna(subset=["latitude", "longitude"])

        if df_validos.empty:
            st.warning("⚠️ Nenhuma coordenada válida encontrada. Mapa centralizado no Brasil.")
            mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
            st_folium(mapa, width=800, height=600)
            return

        # Centralizar no meio dos pontos válidos
        lat_center = df_validos["latitude"].mean()
        lon_center = df_validos["longitude"].mean()
        mapa = folium.Map(location=[lat_center, lon_center], zoom_start=5)

        pontos_plotados = 0

        # Adicionar os marcadores
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
            pontos_plotados += 1

        st.success(f"✅ {pontos_plotados} ponto(s) plotado(s) no mapa!")
        st_folium(mapa, width=800, height=600)

    except Exception as e:
        st.error("❌ Erro ao carregar os dados do mapa.")
        st.exception(e)
