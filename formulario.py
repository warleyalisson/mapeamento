import streamlit as st
import datetime

def formulario_envio(sheet):
    st.subheader("📍 Adicionar novo ponto de cultivo")

    # Obter todos os registros existentes para determinar o próximo ID
    registros = sheet.get_all_records()
    proximo_id = len(registros) + 1 if registros else 1

    with st.form("formulario"):
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        relato = st.text_area("Relato sobre o cultivo")
        referencia = st.text_input("Referência (opcional)")
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
