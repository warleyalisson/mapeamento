import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Função para carregar dados da planilha com cache
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

# Função para exibir o mapa com tratamento completo de coordenadas
def exibir_mapa(sheet):
    st.subheader("🗺️ Mapa de pontos cadastrados")

    df = carregar_dados(sheet)

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    # Checar colunas essenciais
    colunas_necessarias = ["latitude", "longitude", "endereco_completo", "relato", "telefone_contato", "email_contato"]
    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            st.warning(f"⚠️ Coluna '{coluna}' não encontrada.")
            return

    # Correção e normalização de latitude/longitude
    df["latitude"] = df["latitude"].astype(str).str.replace(",", ".", regex=False)
    df["longitude"] = df["longitude"].astype(str).str.replace(",", ".", regex=False)

    # Forçar conversão para float
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Filtrar coordenadas válidas
    df_validos = df[
        df["latitude"].between(-90, 90) &
        df["longitude"].between(-180, 180)
    ].dropna(subset=["latitude", "longitude"])

    total_pontos = len(df)
    pontos_validos = len(df_validos)
    pontos_invalidos = total_pontos - pontos_validos

    st.info(f"🔍 {total_pontos} ponto(s) carregado(s), {pontos_validos} válido(s), {pontos_invalidos} ignorado(s).")

    if pontos_validos == 0:
        st.warning("⚠️ Nenhum ponto válido para exibir no mapa. Mapa centralizado no Brasil.")
        mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
        st_folium(mapa, width=800, height=600)
        return

    # Mapa centralizado na média dos pontos
    lat_center = df_validos["latitude"].mean()
    lon_center = df_validos["longitude"].mean()
    mapa = folium.Map(location=[lat_center, lon_center], zoom_start=5)

    # Adiciona os marcadores válidos
    for _, row in df_validos.iterrows():
        popup_html = f"""
        <b>📍 Endereço:</b> {row.get('endereco_completo', 'Não informado')}<br>
        <b>🌱 Relato:</b> {row.get('relato', 'Sem relato')}<br>
        <b>📞 Telefone:</b> {row.get('telefone_contato', 'Não informado')}<br>
        <b>✉️ E-mail:</b> {row.get('email_contato', 'Não informado')}
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_html, max_width=350),
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)

    st_folium(mapa, width=800, height=600)

