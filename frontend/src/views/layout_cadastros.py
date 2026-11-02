import streamlit as st

from components.tab import TabComponent
from views.pages.empresa import EmpresaPage
from views.pages.setor import SetorPage
from views.pages.usuario.usuario import UsuarioPage
from views.pages.cliente import ClientePage
from views.pages.fornecedor import FornecedorPage
from views.pages.rnc.codigo_nc import CodigoNCPage

class LayoutCadastros:
    def __init__(self):
        self.ABA_ATIVA_KEY = "aba_ativa_cadastros"

    def renderizar(self):
        empresa, user, cliente, fornecedor, setor, codigo_nc = TabComponent(lista_tab=["Empresa", "Usuários", "Clientes", "Fornecedores", "Setores", "Códigos Não Conformidade"], key="tab_cadastros").tabs()

        with empresa:
            EmpresaPage().renderizar()

        with user:
            UsuarioPage().renderizar()

        with cliente:
            ClientePage().renderizar()

        with fornecedor:
            FornecedorPage().renderizar()

        with setor:
            SetorPage().renderizar()
        
        with codigo_nc:
            CodigoNCPage().renderizar()
