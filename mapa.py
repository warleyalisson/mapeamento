import folium
from streamlit_folium import st_folium

def exibir_mapa(df):
    # Sempre cria o mapa (mesmo se não houver marcações ainda)
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    if not df.empty:
        for _, row in df.iterrows():
            try:
                # Corrige vírgula para ponto
                lat = float(str(row["latitude"]).replace(",", "."))
                lon = float(str(row["longitude"]).replace(",", "."))

                # Verifica se latitude e longitude são válidos
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue

                # Monta o texto do popup
                popup = ""
                if "relato" in row and row["relato"]:
                    popup += f"<b>Relato:</b> {row['relato']}<br>"
                if "referencia" in row and row["referencia"]:
                    popup += f"<b>Referência:</b> {row['referencia']}<br>"
                if "data_adicao" in row and row["data_adicao"]:
                    popup += f"<b>Data:</b> {row['data_adicao']}"

                # Adiciona o marcador ao mapa
                folium.Marker(
                    location=[lat, lon],
                    popup=popup if popup else "Ponto cadastrado",
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(mapa)

            except Exception as e:
                print(f"[⚠️] Erro ao processar ponto: {e}")

    # Sempre renderiza o mapa, mesmo vazio
    st_folium(mapa, width=900, height=600)
