import streamlit as st
from components.button import ButtonComponent
from components.divider import Divider

class TitlePages:
    def __init__(self, title_page:str=None, btn_nome:str=None, acao_btn = None, parametro_acao = None):
        self.title_page = title_page
        self.btn_nome = btn_nome
        self.acao_btn = acao_btn
        self.parametro_acao = parametro_acao
    
    def title(self):
        title_col, espaco, btn_col = st.columns([2, 4, 2], vertical_alignment="bottom")
        with title_col:
            st.write(f"## {self.title_page}")
        with btn_col:
            ButtonComponent(label=self.btn_nome, onclick=self.acao_btn, args=[self.parametro_acao]).btn()
        
        Divider().divider()
        