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
                # Montar endereço completo com número
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

    with st.form("formulario_cadastro"):
        st.markdown("**Preencha os dados do cultivo e localização:**")

        cep_input = st.text_input("CEP *", max_chars=20)
        numero = st.text_input("Número da casa *")
        relato = st.text_area("Relato sobre o cultivo *", placeholder="Descreva brevemente o cultivo")
        referencia = st.text_input("Referência (opcional)")
        telefone_contato = st.text_input("📞 Telefone/WhatsApp (opcional)")
        email_contato = st.text_input("✉️ E-mail *")

        enviar = st.form_submit_button("Salvar ponto")

        if enviar:
            # Validações
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
                # Buscar endereço completo via ViaCEP
                endereco = buscar_endereco_completo(cep, numero)
                if endereco:
                    # Geocodificar via Google Maps
                    latitude, longitude, endereco_formatado = geocodificar_googlemaps(endereco)

                    if latitude and longitude:
                        # Mostrar mapa
                        st.success(f"✅ Localização encontrada: {endereco_formatado}")
                        mapa = folium.Map(location=[latitude, longitude], zoom_start=17)
                        folium.Marker(
                            location=[latitude, longitude],
                            popup=endereco_formatado,
                            icon=folium.Icon(color="green", icon="leaf")
                        ).add_to(mapa)
                        st_folium(mapa, width=700, height=500)

                        # Salvar no banco
                        data = datetime.datetime.now().strftime("%Y-%m-%d")
                        nova_linha = [
                            proximo_id,
                            cep,
                            endereco_formatado,
                            "",  # Complemento (não usado)
                            latitude,
                            longitude,
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
                            st.experimental_rerun()
                        except Exception as e:
                            st.error("❌ Erro ao salvar os dados.")
                            st.exception(e)
                    else:
                        st.error("❌ Endereço não localizado. Verifique CEP e número.")
                else:
                    st.error("❌ Não foi possível consultar o CEP informado.")
