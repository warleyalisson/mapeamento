import gspread
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def conectar_planilha(sheet_name="Mapa Araruta - PANC (colaborativo)", worksheet_name="DB_mapa"):
    escopos = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopos)
    cliente = gspread.authorize(credenciais)

    # Abrir a planilha pelo nome exato
    planilha = cliente.open(sheet_name)
    return planilha.worksheet(worksheet_name)
