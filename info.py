import streamlit as st
import pandas as pd
from google_auth import conectar_planilha

# Função para exibir informações gerais e de contato
def exibir_informacoes():
    st.subheader("📚 Sobre a Araruta como PANC")
    
    st.markdown("""
A Araruta (Maranta arundinacea) é uma planta alimentícia não convencional (PANC) conhecida pelo seu rizoma rico em amido de alta digestibilidade, livre de glúten e muito valorizado nutricionalmente.

Esta plataforma visa mapear pontos de cultivo da Araruta e facilitar o acesso a informações sobre onde encontrar, plantar e utilizar esta PANC de grande potencial para a segurança alimentar e diversidade agrícola.
    """)

    st.markdown("---")
    st.subheader("🔎 Locais e Contatos para Encontrar a Araruta")

    # Definições da planilha
    NOME_PLANILHA_ID = "1anS4eByA0hTI4w_spDIDPS3P205czV2f74N63UvOioM"
    NOME_ABA = "Página1"

    try:
        # Conectar e carregar os dados
        aba_dados = conectar_planilha(NOME_PLANILHA_ID, NOME_ABA)
        registros = aba_dados.get_all_records()
        df = pd.DataFrame(registros)

        if not df.empty:
            # Percorrer cada ponto cadastrado
            for _, row in df.iterrows():
                st.markdown(f"### 🌱 Cultivo #{row.get('id', '')}")
                
                endereco_cultivo = row.get('endereco_completo', '').strip()
                endereco_contato = row.get('endereco_contato', '').strip()
                telefone_contato = row.get('telefone_contato', '').strip()
                email_contato = row.get('email_contato', '').strip()

                # Mostrar endereço do cultivo
                if endereco_cultivo:
                    st.markdown(f"📍 **Endereço do Cultivo:** {endereco_cultivo}")

                # Mostrar informações de contato
                if endereco_contato:
                    st.markdown(f"🏡 **Endereço de Contato:** {endereco_contato}")
                if telefone_contato:
                    st.markdown(f"📞 **Telefone/WhatsApp:** {telefone_contato}")
                if email_contato:
                    st.markdown(f"✉️ **E-mail:** {email_contato}")

                st.markdown("---")  # Separador visual entre os registros
        else:
            st.info("Nenhum ponto de cultivo foi cadastrado ainda.")

    except Exception as e:
        st.error("❌ Erro ao carregar as informações.")
        st.exception(e)
