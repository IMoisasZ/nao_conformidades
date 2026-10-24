import streamlit as st

from components.input import InputComponent
from components.button import ButtonComponent
from views.pages.dados_iniciais import DadosInciais
class HeaderComponent:
    def __init__(self, label:str="nome_header", divider:bool=False, width="stretch", text_alignment:str="center"):
        self.label = label
        self.divider = divider
        self.width = width
        self.text_alignment = text_alignment
        self.NOME_BTN_RNC = "nome_btn_rnc"

        if self.NOME_BTN_RNC not in st.session_state:
            st.session_state[self.NOME_BTN_RNC] = "Lista RNC"


    def header_rnc(self):
        img, header = st.columns([1,5])
        with img:
            st.image("static/logo_injetaq.png")
        with header:    
            self.header = st.header(body=self.label, divider=self.divider, width=self.width, text_alignment=self.text_alignment)
        
        dados_rnc, dados_data, dados_status, btn_lista_rnc_col, btn_salvar = st.columns([1,1,2,1,1], vertical_alignment="bottom")
        with dados_rnc:
            rnc_numero = InputComponent(label="Numero RNC", disabled=True, ).input()
        with dados_data:
            data_rnc = InputComponent(label="Data", disabled=True).input()
        with dados_status:
            status = InputComponent(label="Status", disabled=True, value="Aguardando resposta").input()
        with btn_lista_rnc_col:
            args_btn = "lista" if st.session_state[self.NOME_BTN_RNC] == "Lista RNC" else "cadastro"
            btn_lista = ButtonComponent(label="Lista RNC" if args_btn == "lista" else "Cadastrar RNC", onclick=self.listar_rnc, args=[args_btn]).btn()
        with btn_salvar:
            btn_salvar = ButtonComponent(label="Salvar").btn()

    def header_padrao(self):
        img, header = st.columns([1,5])
        with img:
            st.image("static/logo_injetaq.png")
        with header:
            return st.header(body=self.label, divider=self.divider, width=self.width, text_alignment=self.text_alignment)

    def listar_rnc(self, status:str):
        if status == "lista":
            st.session_state[self.NOME_BTN_RNC] = "Cadastrar RNC"
        else:
            st.session_state[self.NOME_BTN_RNC] = "Lista RNC"
        DadosInciais().mudar_tela(view=status)

