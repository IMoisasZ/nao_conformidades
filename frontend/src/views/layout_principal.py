import streamlit as st

from views.layout_menu import LayoutMenu
from views.layout_cadastros import LayoutCadastros
from views.layout_rnc import LayoutRnc
from views.pages.lista_rnc import ListaRnc

from components.header import HeaderComponent

class LayoutPrincipal:
    def __init__(self):
        self.PAGINA_ATIVA = "pagina_ativa"
        if self.PAGINA_ATIVA not in st.session_state:
            st.session_state[self.PAGINA_ATIVA] = "RNC"

    def renderizar(self):
        LayoutMenu().renderizar()
        HeaderComponent(label="Relatório de Não Conformidade - (RNC)").header_padrao()

        pagina = st.session_state[self.PAGINA_ATIVA]

        if pagina == "Cadastros":
            LayoutCadastros().renderizar()
        elif pagina == "RNC":
            LayoutRnc().renderizar()
        elif pagina == "Lista RNC":
            ListaRnc().renderizar()