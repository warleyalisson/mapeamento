import folium
from streamlit_folium import st_folium

def exibir_mapa(df):
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    for _, row in df.iterrows():
        try:
            lat = float(str(row["latitude"]).replace(",", "."))
            lon = float(str(row["longitude"]).replace(",", "."))

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue

            popup = ""
            if "relato" in row and row["relato"]:
                popup += f"<b>Relato:</b> {row['relato']}<br>"
            if "referencia" in row and row["referencia"]:
                popup += f"<b>Referência:</b> {row['referencia']}<br>"
            if "data_adicao" in row and row["data_adicao"]:
                popup += f"<b>Data:</b> {row['data_adicao']}"

            folium.Marker(
                location=[lat, lon],
                popup=popup,
                icon=folium.Icon(color="green", icon="leaf")
            ).add_to(mapa)

        except Exception as e:
            print(f"[⚠️] Erro ao processar ponto: {e}")

    st_folium(mapa, width=900, height=600)

        except Exception as e:
            print(f"[⚠️] Erro ao processar ponto: {e}")

    # Exibe o mapa interativo no Streamlit
    st_folium(mapa, width=900, height=600)
