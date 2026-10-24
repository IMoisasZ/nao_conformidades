import streamlit as st
from components.button import ButtonComponent

class LayoutMenu:
    def renderizar(self):
        with st.sidebar:
            st.title("📌 Menu Principal")
            st.divider()

            # Botão para abrir o Layout de Cadastros (Abas)
            if ButtonComponent(
                label="📁 Cadastros Gerais", 
                key="btn_menu_cadastros",
                width="stretch"
            ).btn():
                st.session_state["pagina_ativa"] = "Cadastros"
                st.rerun()


            # Botão para abrir a RNC (Abas)
            if ButtonComponent(
                label="📝 RNC", 
                key="btn_menu_rnc",
                width="stretch"
            ).btn():
                st.session_state["pagina_ativa"] = "RNC"
                st.rerun()


            # Botão para abrir a Listagem Geral de RNCs
            if ButtonComponent(
                label="📋 Consultar RNCs", 
                key="btn_menu_lista_rnc",
                width="stretch"
            ).btn():
                st.session_state["pagina_ativa"] = "Lista RNC"
                st.rerun()

            st.divider()
            st.caption("Sistema de Gestão de RNC v1.0")