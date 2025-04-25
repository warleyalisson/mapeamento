import folium
from streamlit_folium import st_folium

def exibir_mapa(df):
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)
    for _, row in df.iterrows():
        popup = f"<b>Relato:</b> {row['relato']}<br><b>Referência:</b> {row['referencia']}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)
    st_folium(mapa, width=900, height=600)
