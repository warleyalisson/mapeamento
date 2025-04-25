import streamlit as st
import datetime

def formulario_envio(sheet):
    st.subheader("📍 Adicionar novo ponto de cultivo")

    with st.form("formulario"):
        id_valor = st.number_input("ID (número inteiro)", step=1, format="%d")
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        relato = st.text_area("Relato sobre o cultivo")
        referencia = st.text_input("Referência (opcional)")
        enviar = st.form_submit_button("Enviar")

        if enviar:
            data = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [id_valor, latitude, longitude, relato, referencia, data]

            try:
                sheet.append_row(nova_linha)
                st.success("✅ Ponto adicionado com sucesso!")
            except Exception as e:
                st.error("❌ Erro ao salvar os dados.")
                st.exception(e)
