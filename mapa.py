import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

def geocodificar_endereco(endereco):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    try:
        location = geolocator.geocode(endereco + ", Brasil", timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"[⚠️] Erro ao geocodificar endereço: {e}")
        return None, None

def exibir_mapa(df):
    mapa = folium.Map(location=[-14.2, -51.9], zoom_start=4)

    if df.empty:
        st.warning("⚠️ Nenhum ponto cadastrado ainda.")
    else:
        for index, row in df.iterrows():
            try:
                # Primeiro tenta usar o endereço completo
                endereco = row.get("endereco_completo", "").strip()

                # Se não tiver endereço, tenta usar o CEP
                if not endereco:
                    endereco = row.get("cep", "").strip()

                if not endereco:
                    continue  # Se não tiver nenhum dos dois, pula

                # Geocodifica o endereço/cep
                lat, lon = geocodificar_endereco(endereco)
                time.sleep(1)  # respeitar limites do Nominatim

                if lat and lon:
                    # Monta o popup bonito
                    popup_text = ""
                    if "relato" in row and row["relato"]:
                        popup_text += f"<b>Relato:</b> {row['relato']}<br>"
                    if "referencia" in row and row["referencia"]:
                        popup_text += f"<b>Referência:</b> {row['referencia']}<br>"
                    if "data_adicao" in row and row["data_adicao"]:
                        popup_text += f"<b>Data:</b> {row['data_adicao']}"

                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_text if popup_text else "Ponto sem descrição",
                        icon=folium.Icon(color="green", icon="leaf")
                    ).add_to(mapa)

            except Exception as e:
                print(f"[⚠️] Erro ao processar linha {index}: {e}")

    st_folium(mapa, width=900, height=600)

