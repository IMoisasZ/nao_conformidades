import streamlit as st

from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from components.input import InputComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider

class FornecedorPage:
    def __init__(self):
        self.CADASTRO_FORNECEDOR = "cadastro_fornecedor"
        self.EDITANDO_FORNECEDOR = "editando_fornecedor"
        self.message = MensagemComponent(key_prefix="fornecedor")

        if self.CADASTRO_FORNECEDOR not in st.session_state:
            st.session_state[self.CADASTRO_FORNECEDOR] = False

        if self.EDITANDO_FORNECEDOR not in st.session_state:
            st.session_state[self.EDITANDO_FORNECEDOR] = None

    def rendereizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_FORNECEDOR]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_FORNECEDOR)
        is_edicao = editando is not None

        if is_edicao:
            fornecedor_dados = editando.get("dados")

            if hasattr(fornecedor_dados, "id"):
                id_padrao = fornecedor_dados.id
                nome_padrao = getattr(fornecedor_dados, "nome_fornecedor", "")
                ativo_padrao = getattr(fornecedor_dados, "ativo", True)
            elif isinstance(fornecedor_dados, dict):
                id_padrao = fornecedor_dados.get("id")
                nome_padrao = fornecedor_dados.get("nome_fornecedor") or fornecedor_dados.get("Fornecedor") or ""
                ativo_padrao = fornecedor_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            if "input_fornecedor" not in st.session_state:
                st.session_state["input_fornecedor"] = ""

            if "checkbox_fornecedor" not in st.session_state:
                st.session_state["checkbox_fornecedor"] = True

        titulo_pagina = f"Editar fornecedor: {nome_padrao}" if is_edicao else "Cadastrar fornecedor"
        TitlePages(title_page=titulo_pagina,btn_nome="Lista de fornecedores", acao_btn=self.mudar_tela, parametro_acao=False).title()

        if id_padrao and st.session_state.get("fornecedor_carregado_id") != id_padrao:
            st.session_state["input_fornecedor"] = nome_padrao
            st.session_state["checkbox_fornecedor"] = ativo_padrao
            st.session_state["fornecedor_carregado_id"] = id_padrao

        fornecedor_col, ativo_col, espaco = st.columns([4,2,4], vertical_alignment="bottom")
        with fornecedor_col:
            fornecedor = InputComponent(label="Fornecedor", key="input_fornecedor").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", key="checkbox_ativo", disabled=False if is_edicao else True, value=st.session_state.get("checkbox_ativo", True)).checkbox()

        Divider(color="gray").divider()

        btn_cadastrar_col, btn_novo_col = st.columns(2)
        with btn_cadastrar_col:
            ButtonComponent(label="Cadastrar fornecedor").btn()
        with btn_novo_col:
            ButtonComponent(label="Novo").btn()

    def lista_view(self):
        TitlePages(title_page="Lista de fornecedores",btn_nome="Cadastrar fornecedor", acao_btn=self.mudar_tela, parametro_acao=True).title()
        dados_fornecedor = [
            {
                "ID": "",
                "Fornecedor": "",
                "Ativo": ""
            }
        ]

        st.dataframe(data=dados_fornecedor)

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_FORNECEDOR] = status
        st.rerun()

    def limpar_dados(self):
        pass