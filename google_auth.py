import gspread
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def conectar_planilha(sheet_name="Mapa Araruta - PANC (colaborativo)", worksheet_name="DB_mapa"):
    """
    Conecta a uma planilha do Google Sheets e retorna a aba (worksheet) desejada.

    Parâmetros:
    - sheet_name: nome exato da planilha no Google Drive.
    - worksheet_name: nome exato da aba (guia) da planilha.

    Retorna:
    - worksheet: objeto da aba conectada para leitura/escrita de dados.
    """

    escopos = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Carrega as credenciais do secret configurado no Streamlit Cloud
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

    # Cria as credenciais e cliente gspread
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopos)
    cliente = gspread.authorize(credenciais)

    # Abre a planilha e retorna a worksheet desejada
    planilha = cliente.open(sheet_name)
    worksheet = planilha.worksheet(worksheet_name)
    return worksheet
