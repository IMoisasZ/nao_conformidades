import streamlit as st

from components.title_page import TitlePages

class HorasUtilizadas:
    def __init__(self):
        self.CADASTRAR_HRS_UTILIZADAS = "cadastrar_hrs_utilizadas"
        self.EDITANDO_HRS_UTILIZADAS = "editando_hrs_utilizadas"

        if self.CADASTRAR_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = True

        if self.EDITANDO_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.EDITANDO_HRS_UTILIZADAS] = None

    @st.dialog("Horas Utilizadas na RNC")
    def renderizar(self):
        st.selectbox(label="Operação", options=["Projeto", "Plano de Metodos", "CAD/CAM", "Modelação", "Usinagem 2D"])
        st.text_input(label="Qtde horas")

        st.dataframe(data=[{"Operação": "", "Qtde horas":""}])

        col_btn_incluir, col_btn_remover = st.columns(2)
        with col_btn_incluir:
            st.button(label="Incluir horas", width="stretch", type="primary")
        with col_btn_remover:
            st.button(label="Remover horas", width="stretch", type="secondary")

    def cadastro_view(self):
        titulo_pagina = ""
        TitlePages(title_page=titulo_pagina, btn_nome="Voltar para RNC", acao_btn=self.mudar_tela, parametro_acao=False).title()

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = status