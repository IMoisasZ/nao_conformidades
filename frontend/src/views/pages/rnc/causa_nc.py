import streamlit as st

from components.text_area import TextAreaComponent
from components.input import InputComponent

class CausaNc:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {"imagens": []}

    def redenrizar(self):
        causa_nc = TextAreaComponent(label="Cuasa da não Conformidade").text_area
        reponsavel_col, data_col, espaco = st.columns([2,1,2])
        with reponsavel_col:
            responsavel = InputComponent(label="Responsável", disabled=True).input()
        with data_col:
            data = InputComponent(label="Data", disabled=True).input()