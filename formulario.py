import streamlit as st
import datetime
import requests
import re
from streamlit_folium import st_folium
import folium

# -------------------------------------------
# Configurações Globais
# -------------------------------------------

# Sua chave de API do Google Maps
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# Expressões Regulares para validações
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$"
TELEFONE_REGEX = r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$"

# -------------------------------------------
# Funções auxiliares
# -------------------------------------------

# Buscar endereço no ViaCEP
def buscar_endereco_via_cep(cep):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                return dados
    except:
        pass
    return None

# Geocodificar endereço usando Google Maps API
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
    except:
        pass
    return None, None, None

# -------------------------------------------
# Formulário de cadastro principal
# -------------------------------------------

def formulario_envio(sheet):
    st.subheader("📍 Cadastro de novo ponto de cultivo")

    # Buscar quantidade atual de registros para definir o próximo ID
    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    # Inicializar Session State para controle dos campos
    campos_iniciais = [
        "latitude", "longitude", "endereco_formatado",
        "cep", "relato", "referencia",
        "telefone_contato", "email_contato",
        "cep_input", "numero"
    ]
    for var in campos_iniciais:
        if var not in st.session_state:
            st.session_state[var] = ""

    # -------------------------------------------
    # Formulário de entrada de dados
    # -------------------------------------------

    with st.form("formulario_cadastro"):
        st.markdown("### 📝 Informações do Cultivo")
        relato = st.text_area("Relato sobre o cultivo *", value=st.session_state.relato, placeholder="Descreva brevemente o local e a experiência")
        referencia = st.text_input("Referência (opcional)", value=st.session_state.referencia)

        st.markdown("### 📬 Informações de Contato")
        telefone_contato = st.text_input("📞 Telefone (ex: (31)91234-5678)", value=st.session_state.telefone_contato)
        email_contato = st.text_input("✉️ E-mail *", value=st.session_state.email_contato)

        st.markdown("### 📌 Localização")
        cep_input = st.text_input("CEP *", max_chars=9, value=st.session_state.cep_input)
        numero = st.text_input("Número da residência *", value=st.session_state.numero)

        buscar = st.form_submit_button("🔎 Buscar localização")

    # -------------------------------------------
    # Lógica de busca e validação
    # -------------------------------------------

    if buscar:
        erros = []
        telefone = telefone_contato.strip()
        email = email_contato.strip()
        cep = ''.join(filter(str.isdigit, cep_input.strip()))

        # Validar campos obrigatórios
        if not relato.strip():
            erros.append("⚠️ O campo 'Relato' é obrigatório.")
        if not numero.strip():
            erros.append("⚠️ Informe o número da residência.")
        if len(cep) != 8:
            erros.append("⚠️ O CEP deve conter 8 dígitos.")
        if telefone and not re.match(TELEFONE_REGEX, telefone):
            erros.append("⚠️ Telefone inválido. Use o formato (31)91234-5678.")
        if not email or not re.match(EMAIL_REGEX, email):
            erros.append("⚠️ E-mail inválido.")

        # Exibir erros encontrados
        if erros:
            for erro in erros:
                st.warning(erro)
        else:
            endereco_cep = buscar_endereco_via_cep(cep)
            if endereco_cep:
                logradouro = endereco_cep.get("logradouro", "")
                bairro = endereco_cep.get("bairro", "")
                cidade = endereco_cep.get("localidade", "")
                uf = endereco_cep.get("uf", "")
                endereco_completo = f"{logradouro} {numero}, {bairro}, {cidade} - {uf}, {cep}, Brasil"

                lat, lon, endereco_formatado = geocodificar_googlemaps(endereco_completo)

                if lat and lon:
                    st.session_state.latitude = round(lat, 7)
                    st.session_state.longitude = round(lon, 7)
                    st.session_state.endereco_formatado = endereco_formatado
                    st.session_state.cep = cep
                    st.session_state.relato = relato
                    st.session_state.referencia = referencia
                    st.session_state.telefone_contato = telefone
                    st.session_state.email_contato = email
                    st.session_state.cep_input = cep_input
                    st.session_state.numero = numero
                    st.success(f"📍 Localização confirmada: {endereco_formatado}")
                else:
                    st.error("❌ Não foi possível obter a localização via Google Maps.")
            else:
                st.error("❌ CEP inválido ou não encontrado no ViaCEP.")

    # -------------------------------------------
    # Visualizar mapa e salvar cadastro
    # -------------------------------------------

    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### 🗺️ Confirme a localização no mapa")

        mapa = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=17)
        folium.Marker(
            location=[st.session_state.latitude, st.session_state.longitude],
            popup=st.session_state.endereco_formatado,
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)
        st_folium(mapa, width=800, height=500)

        if st.button("✅ Confirmar e salvar"):
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [
                proximo_id,
                st.session_state.cep,
                st.session_state.endereco_formatado,
                "",  # Complemento
                float(st.session_state.latitude),
                float(st.session_state.longitude),
                st.session_state.relato.strip(),
                st.session_state.referencia.strip(),
                data,
                "",  # endereço de contato (opcional)
                st.session_state.telefone_contato.strip(),
                st.session_state.email_contato.strip()
            ]
            try:
                sheet.append_row(nova_linha)
                st.success("✅ Cadastro realizado com sucesso!")

                # 🔄 Limpar todos os campos
                for var in campos_iniciais:
                    if var in st.session_state:
                        del st.session_state[var]

                # 🔄 Atualizar a página
                st.rerun()
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
