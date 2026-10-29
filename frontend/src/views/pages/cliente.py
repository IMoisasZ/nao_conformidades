import streamlit as st

from components.title_page import TitlePages
from components.input import InputComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent

class ClientePage:
    def __init__(self):
        self.CADASTRO_CLIENTE = "cadastro_cliente"
        self.EDITANDO_CLIENTE = "editando_cliente"

        if self.CADASTRO_CLIENTE not in st.session_state:
            st.session_state[self.CADASTRO_CLIENTE] = False

        if self.EDITANDO_CLIENTE not in st.session_state:
            st.session_state[self.EDITANDO_CLIENTE] = None

    def renderizar(self):
        if st.session_state[self.CADASTRO_CLIENTE]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        TitlePages(title_page="Lista de clientes", btn_nome="Lista de clientes", acao_btn=self.mudar_tela, parametro_acao=False).title()

        editando = st.session_state.get(self.EDITANDO_CLIENTE)
        is_edicao = editando is not None


        cliente_col, ativo_col, espaco = st.columns([4,2,4], vertical_alignment="bottom")
        with cliente_col:
            InputComponent(label="Cliente", key="input_cliente").input()
        with ativo_col:
            CheckboxComponent(label="Ativo", key="checkbox_ativo", disabled=False if is_edicao else True, value=True).checkbox()
        btn_incluir_col, btn_novo_col = st.columns(2)
        with btn_incluir_col:
            ButtonComponent(label="Editar cliente" if is_edicao else "Cadastrar cliente", key="btn_cadastrar_cliente").btn()
        with btn_novo_col:
            ButtonComponent(label="Novo", key="btn_novo_cliente").btn()



    def lista_view(self):
        TitlePages(title_page="Lista de clientes", btn_nome="Cadastrar cliente", acao_btn=self.mudar_tela, parametro_acao=True).title()
        dados_cliente = [
            {
                "ID": "",
                "Cliente": "",
                "Ativo": ""
            }
        ]

        st.dataframe(data=dados_cliente)

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_CLIENTE] = status
