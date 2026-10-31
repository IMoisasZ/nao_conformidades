import streamlit as st

from components.mensagem import MensagemComponent
from components.title_page import TitlePages

from backend.src.connection.db_connection import get_db
from backend.src.services.setor_service import SetorService

class UsuarioSetoresPage:
    def __init__(self, usuario_id:int = None, usuario_nome:str = ""):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.message = MensagemComponent()
        self.CADASTRO_USUARIO_SETOR = "cadastro_usuario_setor"
        self.EDITANDO_USUARIO_SETOR = "editando_usuario_setor"

        if self.CADASTRO_USUARIO_SETOR not in st.session_state:
            st.session_state[self.CADASTRO_USUARIO_SETOR] = False

        if self.EDITANDO_USUARIO_SETOR not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO_SETOR] = None

    def renderizar(self):

        lista_setores = self.obter_todos_setores()
        TitlePages(title_page=f"Cadastro de setores em que o usuario {self.usuario_nome} é responsavel")

        st.multiselect(label="Setores", options=lista_setores if lista_setores else [])

    def obter_todos_setores(self):
        try:
            with get_db() as db:
                setores = SetorService.obter_todos_setores(db=db)
                return setores
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar setores: {str(e)}", tipo="error")
            return []