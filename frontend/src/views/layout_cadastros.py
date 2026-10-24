import streamlit as st

from components.tab import TabComponent
from views.pages.empresa import EmpresaPage
from views.pages.setor import SetorPage

class LayoutCadastros:
    def __init__(self):
        pass

    def renderizar(self):
        empresa, user, cliente, fornecedor, setor = TabComponent(lista_tab=["Empresa", "Usuarios", "Clientes", "Fornecedores", "Setores"]).tabs()

        with empresa:
            EmpresaPage().renderizar()
        
        with user:
            pass

        with cliente:
            pass

        with fornecedor:
            pass

        with setor:
            SetorPage().renderizar()
            