import streamlit as st

from components.tab import TabComponent

from views.pages.dados_iniciais import DadosInciais
from views.pages.nao_conformidade import NaoConformidade
from views.pages.imagens import Imagens
from views.pages.disposicao_nc import DisposicaoNc
from views.pages.causa_nc import CausaNc
from views.pages.reinspecao import Reinspecao
from views.pages.plano_acao import PlanoAcao
from views.pages.lista_rnc import ListaRnc
from components.input import InputComponent
from components.button import ButtonComponent

class LayoutRnc:
    def __init__(self):
        self.VIEW_ATIVA = "view_ativa"

        if self.VIEW_ATIVA not in st.session_state:
            st.session_state[self.VIEW_ATIVA] = "lista"

    def renderizar(self):
        if st.session_state[self.VIEW_ATIVA] == "lista":
            return ListaRnc().renderizar()
        self.cadastro_view()

    def cadastro_view(self):
        dados_rnc, dados_data, dados_status, btn_lista_rnc_col, btn_salvar = st.columns([1,1,2,1,1], vertical_alignment="bottom")
        with dados_rnc:
            rnc_numero = InputComponent(label="Numero RNC", disabled=True, ).input()
        with dados_data:
            data_rnc = InputComponent(label="Data", disabled=True).input()
        with dados_status:
            status = InputComponent(label="Status", disabled=True, value="Aguardando resposta").input()
        with btn_lista_rnc_col:
            btn_lista = ButtonComponent(label="Lista RNC", onclick=self.mudar_tela).btn()
        with btn_salvar:
            btn_salvar = ButtonComponent(label="Salvar").btn()

        dados_iniciais, nao_conformidade, imagens, disposicao_nao_conformidade, causa_nao_conformidade, reinspecao, plano_de_acao = TabComponent(["Dados inciais", "Não Conformidade", "Imagens", "Disposição da Não Conformidade", "Causa da Não Conformidade", "Reinspeção", "Plano de Ação"]).tabs()

        with dados_iniciais:
            DadosInciais().renderizar()

        with nao_conformidade:
            NaoConformidade().renderizar()

        with imagens:
            Imagens().renderizar()

        with disposicao_nao_conformidade:
            DisposicaoNc().renderizar()

        with causa_nao_conformidade:
            CausaNc().redenrizar()

        with reinspecao:
            Reinspecao().renderizar()

        with plano_de_acao:
            PlanoAcao().renderizar()

    def mudar_tela(self):
        st.session_state[self.VIEW_ATIVA] = "lista"
        st.rerun()
