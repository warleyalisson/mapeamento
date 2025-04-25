import gspread
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def conectar_planilha(sheet_id="1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM", worksheet_name="DB_mapa"):
    """
    Conecta a uma planilha do Google Sheets usando o ID exclusivo e retorna a aba (worksheet) especificada.

    Parâmetros:
    - sheet_id: ID exclusivo da planilha no Google Sheets.
    - worksheet_name: Nome da aba (worksheet) dentro da planilha.

    Retorna:
    - worksheet: Objeto da aba conectada para operações de leitura/escrita.
    """

    escopos = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Carrega as credenciais do segredo configurado no Streamlit Cloud
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

    # Cria as credenciais e autoriza o cliente gspread
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopos)
    cliente = gspread.authorize(credenciais)

    # Abre a planilha pelo ID e retorna a aba especificada
    planilha = cliente.open_by_key(sheet_id)
    worksheet = planilha.worksheet(worksheet_name)
    return worksheet
