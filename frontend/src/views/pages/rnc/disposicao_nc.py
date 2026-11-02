import streamlit as st

from components.radio import RadioComponent
from components.input import InputComponent
from components.text_area import TextAreaComponent

class DisposicaoNc:
    def __init__(self):
        self.lista_opcoes = ["Retrabalhar", "Selecionar", "Devolver", "Sucatear", "Reclassificar", "Aprovar", "Aceitar (com ou sem reparo) mediante concessão"]
        self.options = self.lista_opcoes
        self.DADOS_RNC = "dados_rnc"
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {"imagens": []}

    def renderizar(self):
        disposicao_itens, concessao_numero = st.columns([7,2])
        with disposicao_itens:
            disposicao_nc = RadioComponent(label="Disposição para a Não Conformidade", options=self.lista_opcoes, horizontal=True).radio
        with concessao_numero:
            concessao = InputComponent(label="Numero consessão", disabled=True if disposicao_nc != "Aceitar (com ou sem reparo) mediante concessão" else False, color="red" if disposicao_nc == "Aceitar (com ou sem reparo) mediante concessão" else None).input()

        descricao_disposicao_selecionada = TextAreaComponent(label="Descrição da disposição selecionada")