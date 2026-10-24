import streamlit as st

from components.checkbox import CheckboxComponent
from components.input import InputComponent

class PlanoAcao:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {"imagens": []}

    def renderizar(self):
        st.write("Plano de ação corretiva")
        chk_plano_acao_col, plano_acao_col, espaco = st.columns([2,1,6], vertical_alignment="center")
        with chk_plano_acao_col:
            chk_plano_acao = CheckboxComponent(label="Foi aberta ação corretiva?").checkbox()
        with plano_acao_col:
            numero_plano_acao = InputComponent(label="Plano de ação Nº", disabled=False if chk_plano_acao else True).input()

        responsavel_col, data_col, espaco = st.columns([2,1,2])
        with responsavel_col:
            responsavel = InputComponent(label="Responsável", disabled=True).input()
        with data_col:
            data = InputComponent(label="Data", disabled=True).input()
        