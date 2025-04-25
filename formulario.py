import streamlit as st
import datetime
from geopy.geocoders import Nominatim

def geocodificar_endereco(endereco):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    location = geolocator.geocode(endereco)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def formulario_envio(sheet):
    st.subheader("📍 Adicionar novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    with st.form("formulario"):
        endereco = st.text_input("Endereço completo (opcional)")
        latitude = st.number_input("Latitude (se não usar endereço)", format="%.6f")
        longitude = st.number_input("Longitude (se não usar endereço)", format="%.6f")
        relato = st.text_area("Relato sobre o cultivo")
        referencia = st.text_input("Referência (opcional)")
        enviar = st.form_submit_button("Enviar")

        if enviar:
            data = datetime.datetime.now().strftime("%Y-%m-%d")

            # Se endereço for informado, tenta geocodificar
            if endereco.strip():
                lat, lon = geocodificar_endereco(endereco)
                if lat is None or lon is None:
                    st.error("❌ Endereço não encontrado. Verifique e tente novamente.")
                    return
            else:
                lat = latitude
                lon = longitude

            nova_linha = [proximo_id, lat, lon, relato, referencia, data]

            try:
                sheet.append_row(nova_linha)
                st.success(f"✅ Ponto #{proximo_id} adicionado com sucesso!")
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
