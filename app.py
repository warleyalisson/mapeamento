import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# URL do CSV exportado da planilha Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM/export?format=csv&gid=0"

def carregar_dados():
    try:
        dados = pd.read_csv(CSV_URL)
        return dados.dropna(subset=['latitude', 'longitude'])
    except Exception as e:
        st.error("Erro ao carregar os dados da planilha.")
        st.exception(e)
        return pd.DataFrame()

def main():
    st.set_page_config(layout="wide")
    st.title("🌱 Mapa Colaborativo da Araruta como PANC")
    st.markdown("Explore os locais de cultivo da **araruta (Maranta arundinacea)** mapeados colaborativamente.")

    dados = carregar_dados()

    # Criação do mapa
    mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

    for _, row in dados.iterrows():
        popup_texto = f"<b>Relato:</b> {row['relato']}<br><b>Referência:</b> {row['referencia']}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_texto,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)

    st_data = st_folium(mapa, width=900, height=600)

if __name__ == "__main__":
    main()
