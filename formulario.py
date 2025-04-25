import streamlit as st
import datetime

def formulario_envio(sheet):
    st.subheader("📍 Adicionar novo ponto de cultivo")
    with st.form("formulario"):
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        relato = st.text_area("Relato sobre o cultivo")
        referencia = st.text_input("Referência (opcional)")
        enviar = st.form_submit_button("Enviar")

        if enviar:
            hoje = datetime.datetime.now().strftime("%Y-%m-%d")
            nova_linha = [latitude, longitude, relato, referencia, hoje]
            sheet.append_row(nova_linha)
            st.success("✅ Ponto adicionado com sucesso!")
