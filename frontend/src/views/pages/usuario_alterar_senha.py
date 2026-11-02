"""Módulo da Página de Alteração de Senha de Usuários (Frontend Streamlit)."""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.schemas.usuario_schema import UsuarioUpdateSenha
from backend.src.services.usuario_service import UsuarioService
from components.mensagem import MensagemComponent
from components.title_page import TitlePages


class UsuarioAlterarSenhaPage:
    def __init__(self, usuario_id: int = None, usuario_nome: str = None):
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome
        self.USUARIO_VIEW_ATUAL = "usuario_view_atual"
        self.message = MensagemComponent(key_prefix="alterar_senha")

        if self.USUARIO_VIEW_ATUAL not in st.session_state:
            st.session_state[self.USUARIO_VIEW_ATUAL] = "alterar_senha"

    def renderizar(self):
        self.message.exibir_mensagem()
        self.cadastro_view()

    def cadastro_view(self):
        TitlePages(
            title_page=f"Alterar senha do usuário: {self.usuario_nome}",
            btn_nome="Voltar para lista de usuários",
            acao_btn=self.mudar_tela,
            parametro_acao="lista",
            tamanho_cols=[8, 1, 1],
        ).title()

        # Envelopa os campos e o botão em um formulário isolado
        with st.form(key="form_alterar_senha_usuario", clear_on_submit=False):
            col_senha, col_conf_senha, col_btn_alterar = st.columns(
                [4, 4, 4], vertical_alignment="bottom"
            )
            with col_senha:
                senha = st.text_input(
                    label="Nova Senha",
                    type="password",
                    key="input_alt_senha_nova",
                    placeholder="Informe a nova senha (5 dígitos)...",
                )
            with col_conf_senha:
                conf_senha = st.text_input(
                    label="Confirmar Nova Senha",
                    type="password",
                    key="input_alt_senha_confirma",
                    placeholder="Confirme a nova senha...",
                )
            with col_btn_alterar:
                btn_alterar = st.form_submit_button(
                    label="Alterar Senha",
                    use_container_width=True,
                    type="primary",
                )

        if btn_alterar:
            senha_str = (senha or "").strip()
            conf_senha_str = (conf_senha or "").strip()

            try:
                if self.validar_senha(senha=senha_str, conf_senha=conf_senha_str):
                    dados_usuario = UsuarioUpdateSenha(
                        id=self.usuario_id, senha=senha_str
                    )
                    self.alterar_senha(dados_usuario=dados_usuario)
            except ValidationError as e:
                msg_erro = e.errors()[0]["msg"]
                self.message.definir_mensagem(
                    f"Erro de validação: {msg_erro}", tipo="error"
                )
            except ValueError as e:
                self.message.definir_mensagem(str(e), tipo="error")
            except Exception as e:
                self.message.definir_mensagem(
                    f"Erro inesperado: {str(e)}", tipo="error"
                )

    def validar_senha(self, senha: str, conf_senha: str) -> bool:
        """Valida as regras de negócio para troca de senha."""
        if not senha:
            self.message.definir_mensagem("Senha não informada.", tipo="error")
            return False
        if len(senha) != 5:
            self.message.definir_mensagem(
                "A senha deve conter exatamente 5 caracteres!", tipo="error"
            )
            return False
        if not conf_senha:
            self.message.definir_mensagem(
                "Confirmação da senha não informada.", tipo="error"
            )
            return False
        if senha != conf_senha:
            self.message.definir_mensagem(
                "As senhas não correspondem!", tipo="error"
            )
            return False
        return True

    def alterar_senha(self, dados_usuario: UsuarioUpdateSenha):
        try:
            with get_db() as db:
                usuario_id = getattr(dados_usuario, "id", None) or getattr(
                    dados_usuario, "usuario_id", None
                )
                nova_senha = dados_usuario.senha

                UsuarioService.alterar_senha(
                    db=db, usuario_id=usuario_id, nova_senha=nova_senha
                )
                st.toast(
                    f"Senha do usuário {self.usuario_nome} alterada com sucesso!",icon="✅"
                )
                self.limpar_campos()
                st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"
                st.rerun()
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao alterar senha: {str(e)}", tipo="error"
            )

    def limpar_campos(self):
        """Zera os inputs de alteração de senha no session_state."""
        st.session_state.pop("input_alt_senha_nova", None)
        st.session_state.pop("input_alt_senha_confirma", None)

    def mudar_tela(self, view: str):
        self.limpar_campos()
        st.session_state[self.USUARIO_VIEW_ATUAL] = view
        st.rerun()