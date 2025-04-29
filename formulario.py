import streamlit as st
import datetime
import requests
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

# Chave da API do Google Maps (já configurada)
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# Função para buscar endereço no ViaCEP
def buscar_endereco_viacep(cep, numero=""):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                logradouro = dados.get("logradouro", "")
                bairro = dados.get("bairro", "")
                cidade = dados.get("localidade", "")
                uf = dados.get("uf", "")

                # Construção aprimorada do endereço
                endereco = f"{logradouro} número {numero.strip()}, {bairro}, {cidade}, {uf}, Brasil"
                return endereco
    except Exception as e:
        print(f"[ViaCEP] Erro: {e}")
    return None

# Função de geocodificação usando Nominatim
def geocodificar_nominatim(endereco):
    try:
        geolocator = Nominatim(user_agent="araruta-mapeamento")
        location = geolocator.geocode(endereco, timeout=10, addressdetails=True)
        if location:
            return location.latitude, location.longitude, location.address
    except Exception as e:
        print(f"[Nominatim] Erro: {e}")
    return None, None, None

# Função de geocodificação usando Google Maps
def geocodificar_googlemaps(endereco):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco.replace(' ', '+')}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                loc = data['results'][0]['geometry']['location']
                return loc['lat'], loc['lng'], data['results'][0]['formatted_address']
            else:
                print("[Google Maps] Nenhum resultado encontrado.")
    except Exception as e:
        print(f"[Google Maps] Erro: {e}")
    return None, None, None

# Função principal do formulário
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
        numero = st.text_input("Número da casa *")
        buscar = st.form_submit_button("Buscar Localização")

        if buscar:
            cep = ''.join(filter(str.isdigit, cep_input))
            if len(cep) != 8:
                st.warning("⚠️ O CEP deve conter exatamente 8 números.")
            else:
                endereco = buscar_endereco_viacep(cep, numero)
                if endereco:
                    # 1ª tentativa: Nominatim
                    lat, lon, endereco_completo = geocodificar_nominatim(endereco)

                    # 2ª tentativa: Google Maps se Nominatim falhar
                    if not lat or not lon:
                        lat, lon, endereco_completo = geocodificar_googlemaps(endereco)

                    if lat and lon:
                        st.session_state.latitude = lat
                        st.session_state.longitude = lon
                        st.session_state.endereco_completo = endereco_completo
                        st.session_state.cep = cep
                        st.success(f"✅ Local encontrado: {endereco_completo}")
                    else:
                        st.error("❌ Endereço não encontrado com base no número informado. Tente confirmar o CEP e o número.")
                else:
                    st.error("❌ Não foi possível localizar o endereço pelo CEP. Verifique se está correto.")

    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### 🗺️ Localização no mapa:")

        mapa = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=17)
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
            st.markdown("---")
            endereco_contato = st.text_input("📍 Endereço de contato (opcional)")
            telefone_contato = st.text_input("📞 Telefone/WhatsApp para contato (opcional)")
            email_contato = st.text_input("✉️ E-mail para contato (opcional)")

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
                        data,
                        endereco_contato.strip(),
                        telefone_contato.strip(),
                        email_contato.strip()
                    ]
                    try:
                        sheet.append_row(nova_linha)
                        st.success(f"✅ Ponto #{proximo_id} cadastrado com sucesso!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("❌ Erro ao salvar os dados.")
                        st.exception(e)
