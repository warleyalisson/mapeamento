import gspread
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def conectar_planilha(sheet_name="Araruta_Mapa"):
    escopos = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credenciais = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopos)
    cliente = gspread.authorize(credenciais)
    planilha = cliente.open(sheet_name)
    return planilha.sheet1
