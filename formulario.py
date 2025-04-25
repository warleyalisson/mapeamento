import streamlit as st
import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

def geocodificar_cep(cep):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    # Faz a busca com Brasil forçado
    busca = f"{cep}, Brasil"
    location = geolocator.geocode(busca)
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return None, None, None

def formulario_envio(sheet):
    st.subheader("📍 Cadastro de novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    # Variáveis de estado
    if "latitude" not in st.session_state:
        st.session_state.latitude = None
    if "longitude" not in st.session_state:
        st.session_state.longitude = None
    if "endereco_completo" not in st.session_state:
        st.session_state.endereco_completo = ""

    with st.form("formulario_busca"):
        st.markdown("**Digite o CEP para localizar automaticamente o ponto:**")
        cep = st.text_input("CEP *", max_chars=20)
        buscar = st.form_submit_button("Buscar Localização")

        if buscar:
            if cep.strip():
                lat, lon, endereco = geocodificar_cep(cep.strip())
                if lat and lon:
                    st.session_state.latitude = lat
                    st.session_state.longitude = lon
                    st.session_state.endereco_completo = endereco
                    st.success(f"✅ Local encontrado: {endereco}")
                else:
                    st.error("❌ Local não encontrado. Verifique o CEP ou adicione complemento manualmente.")
            else:
                st.warning("⚠️ O campo 'CEP' é obrigatório para buscar.")

    # Se já tiver localização encontrada
    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### 🗺️ Localização no mapa:")

        mapa = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=16)
        folium.Marker(
            location=[st.session_state.latitude, st.session_state.longitude],
            popup=st.session_state.endereco_completo,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)
        st_folium(mapa, width=700, height=500)

        with st.form("formulario_confirmar"):
            st.text_input("Endereço localizado *", value=st.session_state.endereco_completo, disabled=True)
            st.text_input("Latitude *", value=str(st.session_state.latitude), disabled=True)
            st.text_input("Longitude *", value=str(st.session_state.longitude), disabled=True)

            relato = st.text_area("Relato sobre o cultivo *", placeholder="Descreva brevemente o cultivo")
            referencia = st.text_input("Referência (opcional)")

            enviar = st.form_submit_button("Salvar ponto")

            if enviar:
                if not relato.strip():
                    st.warning("⚠️ O campo 'Relato sobre o cultivo' é obrigatório.")
                else:
                    data = datetime.datetime.now().strftime("%Y-%m-%d")
                    nova_linha = [
                        proximo_id,
                        cep.strip(),
                        st.session_state.endereco_completo,
                        "",  # Complemento pode ser vazio aqui
                        st.session_state.latitude,
                        st.session_state.longitude,
                        relato.strip(),
                        referencia.strip(),
                        data
                    ]

                    try:
                        sheet.append_row(nova_linha)
                        st.success(f"✅ Ponto #{proximo_id} cadastrado com sucesso!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("❌ Erro ao salvar os dados.")
                        st.exception(e)
