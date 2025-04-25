import folium
from streamlit_folium import st_folium

def exibir_mapa(df):
    # Cria o mapa centralizado no Brasil
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    if df.empty:
        st.warning("⚠️ Nenhum ponto cadastrado ainda.")
    else:
        for index, row in df.iterrows():
            try:
                # Corrige o formato da latitude/longitude
                lat_str = str(row.get("latitude", "")).strip().replace(",", ".")
                lon_str = str(row.get("longitude", "")).strip().replace(",", ".")

                lat = float(lat_str)
                lon = float(lon_str)

                # Validação extra: coordenadas dentro do intervalo esperado
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    print(f"[⚠️] Coordenada inválida ignorada: linha {index}")
                    continue

                # Construção do popup
                popup_text = ""
                if "relato" in row and row["relato"]:
                    popup_text += f"<b>Relato:</b> {row['relato']}<br>"
                if "referencia" in row and row["referencia"]:
                    popup_text += f"<b>Referência:</b> {row['referencia']}<br>"
                if "data_adicao" in row and row["data_adicao"]:
                    popup_text += f"<b>Data:</b> {row['data_adicao']}"

                # Adiciona o marcador
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text if popup_text else "Ponto sem descrição",
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(mapa)

            except Exception as e:
                print(f"[⚠️] Erro ao processar linha {index}: {e}")

    # Exibe o mapa final
    st_folium(mapa, width=900, height=600)
