import streamlit as st

from components.input import InputComponent
from components.button import ButtonComponent
from components.checkbox import CheckboxComponent

class SetorPage:
    def __init__(self):
        self.CADASTRO_SETOR = "cadastro_setor"
        self.EDITANDO_SETOR = "editando_setor"

        if self.CADASTRO_SETOR not in st.session_state:
            st.session_state[self.CADASTRO_SETOR] = False

        if self.EDITANDO_SETOR not in st.session_state:
            st.session_state[self.EDITANDO_SETOR] = None

    def renderizar(self):
        if st.session_state[self.CADASTRO_SETOR]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        title, espaco, btn = st.columns([3,3,1], vertical_alignment="bottom")
        with title:
            st.write("## Cadastro de setor")
        with btn:
            ButtonComponent(label="Lista de setores", onclick=self.mudar_tela, args=[False]).btn()

        st.markdown(
            """
                <div style="border-bottom: 1px orange solid; width: 100%"></div>
            """,
            unsafe_allow_html=True
        )

        setor_col, ativo_col, espaco = st.columns([3,2,3], vertical_alignment="bottom")
        with setor_col:
            setor = InputComponent(label="Setor").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", disabled=True if self.EDITANDO_SETOR else False, value=True).checkbox()

        st.divider()
        
        salvar, novo = st.columns(2)
        with salvar:     
            cadastrar_setor = ButtonComponent(label="Cadastrar setor").btn()
        with novo:
            novo_setor = ButtonComponent(label="Novo").btn()

    def lista_view(self):
        title, espaco, btn = st.columns([3,3,1], vertical_alignment="bottom")
        with title:
            st.write("## Lista de setores")
        with btn:
            ButtonComponent("Cadastro de setor", onclick=self.mudar_tela, args=[True]).btn()
        
        tabela_setores = [
            {"Nome":"", "Ativo": ""}
        ]

        st.dataframe(data=tabela_setores)

    def mudar_tela(self, status:bool = None):
        st.session_state[self.CADASTRO_SETOR] = status
        st.rerun()