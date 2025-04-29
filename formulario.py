import streamlit as st
import datetime
import requests
from streamlit_folium import st_folium
import folium

# Chave da API do Google Maps
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# Função de geocodificação usando apenas Google Maps
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

    with st.form("formulario_cadastro"):
        st.markdown("**Preencha os dados do cultivo e informações de localização:**")

        cep_input = st.text_input("CEP *", max_chars=20)
        numero = st.text_input("Número da casa *")
        relato = st.text_area("Relato sobre o cultivo *", placeholder="Descreva brevemente o cultivo")
        referencia = st.text_input("Referência (opcional)")
        endereco_contato = st.text_input("📍 Endereço de contato (opcional)")
        telefone_contato = st.text_input("📞 Telefone/WhatsApp para contato (opcional)")
        email_contato = st.text_input("✉️ E-mail para contato (opcional)")

        enviar = st.form_submit_button("Salvar ponto")

        if enviar:
            # Validações básicas
            cep = ''.join(filter(str.isdigit, cep_input))
            if len(cep) != 8:
                st.warning("⚠️ O CEP deve conter exatamente 8 números.")
            elif not numero.strip():
                st.warning("⚠️ O campo 'Número da casa' é obrigatório.")
            elif not relato.strip():
                st.warning("⚠️ O campo 'Relato sobre o cultivo' é obrigatório.")
            else:
                # Montar endereço completo
                endereco = f"{numero.strip()}, {cep.strip()}, Brasil"

                # Geocodificar o endereço
                latitude, longitude, endereco_formatado = geocodificar_googlemaps(endereco)

                if latitude and longitude:
                    # Mapa de visualização
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
                        "",  # Complemento vazio por enquanto
                        latitude,
                        longitude,
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
                else:
                    st.error("❌ Não foi possível localizar o endereço informado. Verifique o CEP e o número.")
