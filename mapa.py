import folium
from streamlit_folium import st_folium

def exibir_mapa(df):
    # Inicializa o mapa centralizado no Brasil
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    for _, row in df.iterrows():
        try:
            # Corrige vírgula e converte para número
            lat = float(str(row["latitude"]).replace(",", "."))
            lon = float(str(row["longitude"]).replace(",", "."))

            # Verifica se coordenadas são válidas
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            # Prepara o popup bonito
            popup = "<b>Relato:</b> " + row.get("relato", "Sem relato")
            if "referencia" in row and row["referencia"]:
                popup += f"<br><b>Referência:</b> {row['referencia']}"
            if "data_adicao" in row and row["data_adicao"]:
                popup += f"<br><b>Data:</b> {row['data_adicao']}"

            folium.Marker(
                location=[lat, lon],
                popup=popup,
                icon=folium.Icon(color="green", icon="leaf")
            ).add_to(mapa)

        except Exception as e:
            print(f"[⚠️] Erro ao processar ponto: {e}")

    st_folium(mapa, width=900, height=600)

            print(f"[⚠️] Erro ao processar ponto: {e}")

    # Exibe o mapa interativo no Streamlit
    st_folium(mapa, width=900, height=600)
