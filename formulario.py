import streamlit as st
import datetime
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

def buscar_endereco_viacep(cep, numero=""):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                logradouro = dados.get("logradouro", "")
                bairro = dados.get("bairro", "")
                localidade = dados.get("localidade", "")
                uf = dados.get("uf", "")
                endereco = f"{logradouro}"
if numero.strip():
    endereco += f", {numero.strip()}"
                endereco += f", {bairro}, {localidade} - {uf}"
                return endereco
    except Exception as e:
        print(f"[ViaCEP] Erro: {e}")
    return None

def geocodificar_endereco(endereco):
    geolocator = Nominatim(user_agent="araruta-mapeamento")
    try:
        location = geolocator.geocode(endereco + ", Brasil", timeout=10, addressdetails=True)
        if location:
            return location.latitude, location.longitude, location.address
    except Exception as e:
        print(f"[Geopy] Erro ao geocodificar: {e}")
    return None, None, None

def formulario_envio(sheet):
    st.subheader("📍 Cadastro de novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    if "latitude" not in st.session_state:
        st.session_state.latitude = None
    if "longitude" not in st.session_state:
        st.session_state.longitude = None
    if "endereco_completo" not in st.session_state:
        st.session_state.endereco_completo = ""
    if "cep" not in st.session_state:
        st.session_state.cep = ""

    with st.form("formulario_busca"):
        st.markdown("**Digite o CEP e o número da casa para localizar o ponto:**")
        cep_input = st.text_input("CEP *", max_chars=20)
        numero = st.text_input("Número da casa (opcional)")
        buscar = st.form_submit_button("Buscar Localização")

        if buscar:
            cep = ''.join(filter(str.isdigit, cep_input))
            if len(cep) != 8:
                st.warning("⚠️ O CEP deve conter exatamente 8 números.")
            else:
                endereco = buscar_endereco_viacep(cep, numero)
                if endereco:
                    lat, lon, endereco_completo = geocodificar_endereco(endereco)
                    if lat and lon:
                        st.session_state.latitude = lat
                        st.session_state.longitude = lon
                        st.session_state.endereco_completo = endereco_completo
                        st.session_state.cep = cep
                        st.success(f"✅ Local encontrado: {endereco_completo}")
                    else:
                        st.error("❌ Local não encontrado com base no endereço.")
                else:
                    st.error("❌ Não foi possível localizar o endereço via CEP. Verifique o número.")

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
                        st.session_state.cep,
                        st.session_state.endereco_completo,
                        "",  # Complemento
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
