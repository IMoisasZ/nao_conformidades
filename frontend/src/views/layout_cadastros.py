import streamlit as st

from components.tab import TabComponent
from views.pages.setor import SetorPage

class LayoutCadastros:
    def __init__(self):
        pass

    def renderizar(self):
        user, cliente, fornecedor, setor = TabComponent(lista_tab=["Usuarios", "Clientes", "Fornecedores", "Setores"]).tabs()

        with user:
            pass

        with cliente:
            pass

        with fornecedor:
            pass

        with setor:
            SetorPage().renderizar()
            