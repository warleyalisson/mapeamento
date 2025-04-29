import streamlit as st
import pandas as pd
from google_auth import conectar_planilha

def exibir_informacoes():
    st.subheader("📚 Sobre a Araruta como PANC")
    
    st.markdown("""
A Araruta (Maranta arundinacea) é uma planta alimentícia não convencional (PANC) conhecida pelo seu rizoma, de onde se extrai um amido de alta digestibilidade, livre de glúten e de grande valor nutricional.

Este projeto visa mapear os pontos de cultivo da Araruta, fomentar seu conhecimento e promover o acesso a informações sobre onde encontrar essa cultura no Brasil.
    """)

    st.markdown("---")
    st.subheader("🔎 Informações para contato e localização")

    # Configurações da planilha
    NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
    NOME_ABA = "Página1"

    try:
        aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)

        if not df.empty:
            for _, row in df.iterrows():
                st.markdown(f"### 🌱 Cultivo #{row.get('id', '')}")
                st.markdown(f"📍 **Endereço do Cultivo:** {row.get('endereco_completo', 'Não informado')}")
                
                endereco_contato = row.get('endereco_contato', '').strip()
                telefone_contato = row.get('telefone_contato', '').strip()
                email_contato = row.get('email_contato', '').strip()

                if endereco_contato:
                    st.markdown(f"🏡 **Endereço para contato:** {endereco_contato}")
                if telefone_contato:
                    st.markdown(f"📞 **Telefone/WhatsApp:** {telefone_contato}")
                if email_contato:
                    st.markdown(f"✉️ **E-mail:** {email_contato}")
                
                st.markdown("---")

        else:
            st.info("Nenhuma informação de cultivo cadastrada ainda.")

    except Exception as e:
        st.error("❌ Erro ao carregar as informações da planilha.")
        st.exception(e)
