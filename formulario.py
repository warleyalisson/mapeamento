import streamlit as st
import datetime
import requests
import re
from streamlit_folium import st_folium
import folium

# Chave da API do Google Maps
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# Regex para validar telefone e e-mail
TELEFONE_REGEX = r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$"
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$"

# Buscar endereço completo no ViaCEP
def buscar_endereco_via_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                return dados
    except Exception as e:
        print(f"[ViaCEP] Erro: {e}")
    return None

# Geocodificação precisa com Google Maps
def geocodificar_googlemaps(endereco_completo):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_completo.replace(' ', '+')}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            if dados['results']:
                loc = dados['results'][0]['geometry']['location']
                endereco_formatado = dados['results'][0]['formatted_address']
                return float(loc['lat']), float(loc['lng']), endereco_formatado
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

    # Formulário de preenchimento
    with st.form("formulario_cadastro"):
        st.markdown("**Preencha os dados do cultivo e contato:**")

        relato = st.text_area("Relato sobre o cultivo *", placeholder="Descreva brevemente o cultivo")
        referencia = st.text_input("Referência (opcional)")
        telefone_contato = st.text_input("📞 Telefone/WhatsApp (DDD + número) (opcional)")
        email_contato = st.text_input("✉️ E-mail *")

        st.markdown("**Localização:**")
        cep_input = st.text_input("CEP *", max_chars=9)
        numero = st.text_input("Número da casa *")

        buscar = st.form_submit_button("📍 Buscar Localização")

    if buscar:
        erros = []
        cep = ''.join(filter(str.isdigit, cep_input))

        # Validações básicas
        if len(cep) != 8:
            erros.append("⚠️ O CEP deve conter exatamente 8 números.")
        if not numero.strip():
            erros.append("⚠️ O campo 'Número da casa' é obrigatório.")
        if not relato.strip():
            erros.append("⚠️ O campo 'Relato sobre o cultivo' é obrigatório.")
        if not email_contato.strip() or not re.match(EMAIL_REGEX, email_contato.strip()):
            erros.append("⚠️ E-mail inválido. Ex: exemplo@dominio.com")
        if telefone_contato.strip() and not re.match(TELEFONE_REGEX, telefone_contato.strip()):
            erros.append("⚠️ Telefone inválido. Ex: (31) 98765-4321")

        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            endereco_cep = buscar_endereco_via_cep(cep)
            if endereco_cep:
                logradouro = endereco_cep.get('logradouro', '')
                bairro = endereco_cep.get('bairro', '')
                cidade = endereco_cep.get('localidade', '')
                uf = endereco_cep.get('uf', '')

                # Montar endereço completo
                endereco_completo = f"{logradouro} {numero.strip()}, {bairro}, {cidade} - {uf}, {cep}, Brasil"

                # Buscar coordenadas
                lat, lon, endereco_formatado = geocodificar_googlemaps(endereco_completo)

                if lat is not None and lon is not None:
                    st.session_state.latitude = round(lat, 7)
                    st.session_state.longitude = round(lon, 7)
                    st.session_state.endereco_formatado = endereco_formatado
                    st.session_state.cep = cep
                    st.success(f"✅ Localização encontrada: {endereco_formatado}")
                else:
                    st.error("❌ Não foi possível localizar o endereço no Google Maps.")
            else:
                st.error("❌ CEP inválido ou não encontrado.")

    # Se já tem latitude e longitude válidos, mostrar mapa e botão de confirmar
    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### 🗺️ Visualização no mapa:")

        mapa = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=17)
        folium.Marker(
            location=[st.session_state.latitude, st.session_state.longitude],
            popup=st.session_state.endereco_formatado,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)
        st_folium(mapa, width=800, height=500)

        if st.button("✅ Confirmar e Salvar"):
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [
                proximo_id,
                st.session_state.cep,
                st.session_state.endereco_formatado,
                "",  # Complemento não utilizado
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
                st.rerun()
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
