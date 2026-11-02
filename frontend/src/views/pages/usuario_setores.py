import streamlit as st

from components.button import ButtonComponent
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.select import SelectComponent
from components.title_page import TitlePages

from backend.src.connection.db_connection import get_db
from backend.src.schemas.usuario_setor_schema import UsuarioSetorLoteRequest
from backend.src.services.setor_service import SetorService
from backend.src.services.usuario_setor_service import UsuarioSetorService


class UsuarioSetoresPage:
    def __init__(self, usuario_id: int = None, usuario_nome: str = ""):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.message = MensagemComponent(key_prefix="usuario_setores")
        self.USUARIO_VIEW_ATUAL = "usuario_view_atual"

        if self.USUARIO_VIEW_ATUAL not in st.session_state:
            st.session_state[self.USUARIO_VIEW_ATUAL] = "setores"

    def renderizar(self):
        self.message.exibir_mensagem()
        self.cadastro_view()

    def cadastro_view(self):
        lista_setores_cadastrados = self.obter_todos_setores()
        setores_atuais_usuario = self.obter_todos_usuarios_setores()

        TitlePages(
            title_page=f"Associar setores ao usuário: {self.usuario_nome}",
            btn_nome="Voltar para lista de usuários",
            acao_btn=self.mudar_tela,
            parametro_acao="lista",
            tamanho_cols=[7, 1, 2],
        ).title()

        setor_col, btn_salvar_col = st.columns([7, 1], vertical_alignment="bottom")

        # Dicionário mapeando Nome -> ID do setor
        opcoes_setores = (
            {s.nome_setor: s.id for s in lista_setores_cadastrados}
            if lista_setores_cadastrados
            else {}
        )

        # Nomes dos setores já vinculados ao usuário (pré-selecionados no multiselect)
        nomes_pre_selecionados = [
            s.nome_setor for s in setores_atuais_usuario
        ]

        with setor_col:
            setores_selecionados = SelectComponent(
                label="Setores sob responsabilidade",
                options=opcoes_setores,
                default=nomes_pre_selecionados,
            ).multiselect()

        with btn_salvar_col:
            btn_salvar = st.button(
                label="Salvar Setores", 
                icon="💾", 
                width="stretch"
            )

        if btn_salvar:
            ids_selecionados = []

            if setores_selecionados:
                for item in setores_selecionados:
                    if isinstance(item, int):
                        ids_selecionados.append(item)
                    elif isinstance(item, str) and item in opcoes_setores:
                        ids_selecionados.append(opcoes_setores[item])

            self.salvar_sincronizacao(ids_selecionados)

    def obter_todos_setores(self):
        try:
            with get_db() as db:
                return SetorService.obter_todos_setores(db=db)
        except Exception as e:
            st.error(f"Erro ao carregar setores: {str(e)}")
            return []

    def obter_todos_usuarios_setores(self):
        try:
            with get_db() as db:
                return UsuarioSetorService.obter_todos_usuarios_setores(
                    db=db, usuario_id=self.usuario_id
                )
        except Exception as e:
            st.error(
                f"Erro ao carregar os setores do responsável {self.usuario_nome}: {str(e)}"
            )
            return []

    def salvar_sincronizacao(self, setores_ids: list[int]):
        try:
            payload = UsuarioSetorLoteRequest(
                usuario_id=self.usuario_id, setores_ids=setores_ids
            )
            with get_db() as db:
                UsuarioSetorService.sincronizar_setores_usuario(
                    db=db, dados=payload
                )

            self.message.definir_mensagem("Setores atualizados com sucesso!", tipo="success")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar setores no banco de dados: {str(e)}")

    def mudar_tela(self, view: str):
        st.session_state[self.USUARIO_VIEW_ATUAL] = view