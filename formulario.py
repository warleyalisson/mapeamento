import streamlit as st
import datetime
import requests
from streamlit_folium import st_folium
import folium

# Chave da API do Google Maps
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# Função para buscar endereço detalhado no ViaCEP
def buscar_endereco_completo(cep, numero=""):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                logradouro = dados.get("logradouro", "")
                bairro = dados.get("bairro", "")
                cidade = dados.get("localidade", "")
                uf = dados.get("uf", "")
                endereco = f"{logradouro} {numero.strip()}, {bairro}, {cidade} - {uf}, {cep}, Brasil"
                return endereco
    except Exception as e:
        print(f"[ViaCEP] Erro: {e}")
    return None

# Geocodificação com Google Maps
def geocodificar_googlemaps(endereco):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco.replace(' ', '+')}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                loc = data['results'][0]['geometry']['location']
                endereco_formatado = data['results'][0]['formatted_address']
                return loc['lat'], loc['lng'], endereco_formatado
    except Exception as e:
        print(f"[Google Maps] Erro: {e}")
    return None, None, None

# Função principal do formulário
def formulario_envio(sheet):
    st.subheader("📍 Cadastro de novo ponto de cultivo")

    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    # Inicializar session_state para localização
    for var in ["latitude", "longitude", "endereco_formatado"]:
        if var not in st.session_state:
            st.session_state[var] = None

    with st.form("formulario_cadastro"):
        st.markdown("**Preencha os dados do cultivo e contato:**")
        relato = st.text_area("Relato sobre o cultivo *", placeholder="Descreva brevemente o cultivo")
        referencia = st.text_input("Referência (opcional)")
        telefone_contato = st.text_input("📞 Telefone/WhatsApp (opcional)")
        email_contato = st.text_input("✉️ E-mail *")

        st.markdown("**Localização:**")
        cep_input = st.text_input("CEP *", max_chars=20)
        numero = st.text_input("Número da casa *")

        buscar = st.form_submit_button("📍 Buscar Localização")

    # Processar localização após clique
    if buscar:
        cep = ''.join(filter(str.isdigit, cep_input))
        if len(cep) != 8:
            st.warning("⚠️ O CEP deve conter exatamente 8 números.")
        elif not numero.strip():
            st.warning("⚠️ O campo 'Número da casa' é obrigatório.")
        elif not relato.strip():
            st.warning("⚠️ O campo 'Relato sobre o cultivo' é obrigatório.")
        elif not email_contato.strip():
            st.warning("⚠️ O campo 'E-mail' é obrigatório.")
        else:
            endereco = buscar_endereco_completo(cep, numero)
            if endereco:
                lat, lon, endereco_formatado = geocodificar_googlemaps(endereco)
                if lat and lon:
                    # Salvar no session_state
                    st.session_state.latitude = lat
                    st.session_state.longitude = lon
                    st.session_state.endereco_formatado = endereco_formatado
                    st.session_state.cep = cep
                    st.success(f"✅ Localização encontrada: {endereco_formatado}")
                else:
                    st.error("❌ Endereço não localizado.")
            else:
                st.error("❌ Não foi possível consultar o CEP informado.")

    # Se já tem localização salva, mostrar mapa e botão de salvar
    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### 🗺️ Visualização no mapa:")

        mapa = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=17)
        folium.Marker(
            location=[st.session_state.latitude, st.session_state.longitude],
            popup=st.session_state.endereco_formatado,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)
        st_folium(mapa, width=700, height=500)

        # Botão separado fora do formulário
        if st.button("✅ Confirmar e Salvar"):
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [
                proximo_id,
                st.session_state.cep,
                st.session_state.endereco_formatado,
                "",  # Complemento
                st.session_state.latitude,
                st.session_state.longitude,
                relato.strip(),
                referencia.strip(),
                data,
                "",  # Endereço de contato removido
                telefone_contato.strip(),
                email_contato.strip()
            ]
            try:
                sheet.append_row(nova_linha)
                st.success(f"✅ Ponto #{proximo_id} cadastrado com sucesso!")
                for var in ["latitude", "longitude", "endereco_formatado", "cep"]:
                    st.session_state[var] = None
                st.experimental_rerun()
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
