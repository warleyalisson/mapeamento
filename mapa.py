import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

# 🔑 Sua chave de API do Google
GOOGLE_API_KEY = "AIzaSyAAgehm3dej7CHrt0Z8_I4ll0BhTg00fqo"

# --------------------------------------------
# Função para carregar dados da planilha
# --------------------------------------------
def carregar_dados(sheet):
    if "dados_planilha" not in st.session_state:
        try:
            if hasattr(sheet, "get_all_records"):
                st.session_state["dados_planilha"] = pd.DataFrame(sheet.get_all_records())
            else:
                st.session_state["dados_planilha"] = sheet
            st.success(f"✅ Dados carregados com sucesso ({len(st.session_state['dados_planilha'])} registros).")
        except Exception as e:
            st.error("❌ Erro ao carregar os dados da planilha.")
            st.exception(e)
            st.session_state["dados_planilha"] = pd.DataFrame()
    return st.session_state["dados_planilha"]

# --------------------------------------------
# Geocodificar endereço via Google Maps API
# --------------------------------------------
def geocodificar_googlemaps(endereco_completo):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={endereco_completo.replace(' ', '+')}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            if dados['results']:
                loc = dados['results'][0]['geometry']['location']
                return float(loc['lat']), float(loc['lng'])
    except:
        pass
    return None, None

# --------------------------------------------
# Função principal para exibir o mapa
# --------------------------------------------
def exibir_mapa(sheet):
    st.subheader("🗺️ Mapa de pontos cadastrados")

    df = carregar_dados(sheet)

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    # Verificar colunas essenciais
    colunas_necessarias = ["endereco_completo", "relato", "telefone_contato", "email_contato"]
    for col in colunas_necessarias:
        if col not in df.columns:
            st.warning(f"⚠️ Coluna obrigatória ausente: {col}")
            return

    pontos = []

    for _, row in df.iterrows():
        lat = row.get("latitude")
        lon = row.get("longitude")

        try:
            lat = float(str(lat).replace(",", "."))
            lon = float(str(lon).replace(",", "."))
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                lat, lon = None, None
        except:
            lat, lon = None, None

        if not lat or not lon:
            endereco = row.get("endereco_completo", "")
            lat, lon = geocodificar_googlemaps(endereco)

        if lat and lon:
            pontos.append({
                "latitude": lat,
                "longitude": lon,
                "endereco": row.get("endereco_completo", ""),
                "relato": row.get("relato", "Sem relato"),
                "telefone": row.get("telefone_contato", "Não informado"),
                "email": row.get("email_contato", "Não informado")
            })

    total_pontos = len(df)
    pontos_validos = len(pontos)
    pontos_invalidos = total_pontos - pontos_validos

    st.info(f"🔍 {total_pontos} ponto(s) carregado(s), {pontos_validos} válido(s), {pontos_invalidos} ignorado(s).")

    if pontos_validos == 0:
        st.warning("⚠️ Nenhum ponto válido para exibir no mapa. Mapa centralizado no Brasil.")
        mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
        st_folium(mapa, width=800, height=600)
        return

    lat_center = sum(p["latitude"] for p in pontos) / pontos_validos
    lon_center = sum(p["longitude"] for p in pontos) / pontos_validos
    mapa = folium.Map(location=[lat_center, lon_center], zoom_start=6)

    for p in pontos:
        popup_html = f"""
            <b>📍 Endereço:</b> {p['endereco']}<br>
            <b>📝 Relato:</b> {p['relato']}<br>
            <b>📞 Telefone:</b> {p['telefone']}<br>
            <b>✉️ E-mail:</b> {p['email']}
        """
        folium.Marker(
            location=[p["latitude"], p["longitude"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)

    st_folium(mapa, width=800, height=600)
