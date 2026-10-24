import streamlit as st

from components.radio import RadioComponent
from components.input import InputComponent

class Reinspecao:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {"imagens": []}

    def renderizar(self):
        reinspecao_col, rnc_col, espaco = st.columns([2,1,6])
        with reinspecao_col:
            reinspecao = RadioComponent(label="Reinspeção", options=["Aprovado", "Reprovado"], horizontal=True)
        with rnc_col:
            rnc = InputComponent(label="RNC").input()

        responsavel_col, data_col, espaco = st.columns([2,1,2])
        with responsavel_col:
            responsavel = InputComponent(label="Responsável", disabled=True).input()
        with data_col:
            data = InputComponent(label="Data", disabled=True).input()
        