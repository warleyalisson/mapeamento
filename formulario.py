import streamlit as st
import datetime
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

def geocodificar_cep(cep, complemento=""):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    busca = cep
    if complemento.strip():
        busca += ", " + complemento
    location = geolocator.geocode(busca + ", Brasil")
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return None, None, None

def formulario_envio(sheet):
    st.subheader("📍 Cadastro de novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    with st.form("formulario_busca"):
        st.markdown("**Preencha o CEP para localizar automaticamente o ponto no mapa**")
        cep = st.text_input("CEP *")
        complemento = st.text_input("Complemento de Endereço (opcional)")
        buscar = st.form_submit_button("Buscar Localização")

    latitude = None
    longitude = None
    endereco_completo = ""

    if buscar:
        if cep.strip():
            latitude, longitude, endereco_completo = geocodificar_cep(cep, complemento)

            if latitude and longitude:
                st.success(f"✅ Local encontrado: {endereco_completo}")
                mapa = folium.Map(location=[latitude, longitude], zoom_start=16)
                folium.Marker(
                    location=[latitude, longitude],
                    popup=endereco_completo,
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(mapa)
                st_folium(mapa, width=700, height=500)
            else:
                st.error("❌ Local não encontrado. Verifique o CEP e o complemento de endereço.")
        else:
            st.warning("⚠️ O campo 'CEP' é obrigatório. Preencha antes de buscar.")

    if latitude and longitude:
        with st.form("formulario_confirmar"):
            st.markdown("**Confirme ou complete as informações para finalizar o cadastro:**")

            st.text_input("Endereço encontrado *", value=endereco_completo, disabled=True)
            st.text_input("Latitude *", value=str(latitude), disabled=True)
            st.text_input("Longitude *", value=str(longitude), disabled=True)

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
                        endereco_completo,
                        complemento.strip(),
                        latitude,
                        longitude,
                        relato.strip(),
                        referencia.strip(),
                        data
                    ]

                    try:
                        sheet.append_row(nova_linha)
                        st.success(f"✅ Ponto #{proximo_id} cadastrado com sucesso!")
                    except Exception as e:
                        st.error("❌ Erro ao salvar os dados.")
                        st.exception(e)
