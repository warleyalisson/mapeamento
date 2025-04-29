import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

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
# Função principal para exibir o mapa
# --------------------------------------------
def exibir_mapa(sheet):
    st.subheader("🗺️ Mapa de pontos cadastrados")

    df = carregar_dados(sheet)

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        return

    # Verificar colunas obrigatórias
    colunas_necessarias = ["latitude", "longitude", "endereco_completo", "relato"]
    for col in colunas_necessarias:
        if col not in df.columns:
            st.warning(f"⚠️ Coluna obrigatória ausente: {col}")
            return

    # Conversão segura para float (já estão com ponto)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Filtrar apenas pontos válidos
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

    # Centralizar no centro dos pontos válidos
    lat_center = df_validos["latitude"].mean()
    lon_center = df_validos["longitude"].mean()
    mapa = folium.Map(location=[lat_center, lon_center], zoom_start=6)

    # Criar marcadores
    for _, row in df_validos.iterrows():
        popup = f"""
        <b>📍 Endereço:</b> {row.get('endereco_completo', 'Não informado')}<br>
        <b>📝 Relato:</b> {row.get('relato', 'Sem relato')}<br>
        <b>📞 Telefone:</b> {row.get('telefone_contato', 'Não informado')}<br>
        <b>✉️ Email:</b> {row.get('email_contato', 'Não informado')}
        """
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup, max_width=350),
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(mapa)

    # Exibir mapa no Streamlit
    st_folium(mapa, width=800, height=600)
