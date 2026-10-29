import streamlit as st

from components.tab import TabComponent
from views.pages.empresa import EmpresaPage
from views.pages.setor import SetorPage
from views.pages.usuario import UsuarioPage
from views.pages.cliente import ClientePage

class LayoutCadastros:
    def __init__(self):
        self.ABA_ATIVA_KEY = "aba_ativa_cadastros"

    def renderizar(self):
        empresa, user, cliente, fornecedor, setor = TabComponent(lista_tab=["Empresa", "Usuários", "Clientes", "Fornecedores", "Setores"], key="tab_cadastros").tabs()

        with empresa:
            EmpresaPage().renderizar()

        with user:
            UsuarioPage().renderizar()

        with cliente:
            ClientePage().renderizar()

        with fornecedor:
            pass

        with setor:
            SetorPage().renderizar()
