import streamlit as st

from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from components.divider import Divider
from components.select import SelectComponent
from components.button import ButtonComponent

from backend.src.connection.db_connection import get_db
from backend.src.services.setor_service import SetorService

class UsuarioSetoresPage:
    def __init__(self, usuario_id:int = None, usuario_nome:str = ""):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.message = MensagemComponent()
        self.USUARIO_VIEW_ATUAL = "usuario_view_atual"
        self.EDITANDO_USUARIO_SETOR = "editando_usuario_setor"

        if self.USUARIO_VIEW_ATUAL not in st.session_state:
            st.session_state[self.USUARIO_VIEW_ATUAL] = "setores"

        if self.EDITANDO_USUARIO_SETOR not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO_SETOR] = None

    def renderizar(self):
        lista_setores = self.obter_todos_setores()
        
        TitlePages(title_page=f"Associar setores ao usuário {self.usuario_nome}", btn_nome="Voltar para lista de usuarios", acao_btn=self.mudar_tela, parametro_acao="lista", tamanho_cols=[7, 1, 2]).title()
        setor_col, btn_incluir_col, btn_remover, espaco = st.columns([4,2, 2, 4], vertical_alignment="bottom")
        with setor_col:
            SelectComponent(label="Setores", options={s.nome_setor: s.id for s in lista_setores} if lista_setores else []).multiselect()
        with btn_incluir_col:
            ButtonComponent(label="Incluir").btn()
        with btn_remover:
            ButtonComponent(label="Remover", disabled=True, icon="🗑").btn()

        Divider(color="gray").divider()


    def obter_todos_setores(self):
        try:
            with get_db() as db:
                setores = SetorService.obter_todos_setores(db=db)
                return setores
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar setores: {str(e)}", tipo="error")
            return []

    def mudar_tela(self, view:str):
        st.session_state[self.USUARIO_VIEW_ATUAL] = view