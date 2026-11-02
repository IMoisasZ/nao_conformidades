import streamlit as st

from components.text_area import TextAreaComponent

class NaoConformidade:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {}


    def renderizar(self):
        dados  = st.session_state.get(self.DADOS_RNC, {})
        descricao_nc = TextAreaComponent(label="Descrição da Não conformidade", value=dados["descricao_nc"]).text_area
        dados["descricao_nc"] = descricao_nc