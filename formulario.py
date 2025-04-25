import streamlit as st
import datetime
from geopy.geocoders import Nominatim

def geocodificar_cep_endereco(cep, endereco=""):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    consulta = cep
    if endereco.strip():
        consulta += ", " + endereco
    location = geolocator.geocode(consulta + ", Brasil")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def inverter_geocodificacao(lat, lon):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    location = geolocator.reverse((lat, lon), exactly_one=True)
    if location:
        return location.address
    else:
        return ""

def formulario_envio(sheet):
    st.subheader("📍 Adicionar novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    with st.form("formulario"):
        cep = st.text_input("CEP (preferencial)")
        endereco = st.text_input("Complemento de Endereço (opcional)")
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude (editável)", format="%.6f")
        with col2:
            longitude = st.number_input("Longitude (editável)", format="%.6f")
        relato = st.text_area("Relato sobre o cultivo")
        referencia = st.text_input("Referência (opcional)")

        auto_sync = st.checkbox("🔁 Preencher automaticamente coordenadas pelo CEP/Endereço")

        if auto_sync:
            if cep.strip() and (latitude == 0.0 and longitude == 0.0):
                lat, lon = geocodificar_cep_endereco(cep, endereco)
                if lat and lon:
                    st.session_state["latitude_auto"] = lat
                    st.session_state["longitude_auto"] = lon
                    latitude = lat
                    longitude = lon
            elif latitude != 0.0 and longitude != 0.0 and not cep.strip():
                endereco = inverter_geocodificacao(latitude, longitude)

        enviar = st.form_submit_button("Enviar")

        if enviar:
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [proximo_id, latitude, longitude, relato, referencia, data]

            try:
                sheet.append_row(nova_linha)
                st.success(f"✅ Ponto #{proximo_id} adicionado com sucesso!")
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
