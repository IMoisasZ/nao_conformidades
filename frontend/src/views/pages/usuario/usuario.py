"""Módulo da Página de Usuários (Frontend Streamlit)."""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.models.usuario_model import TipoUsuario
from backend.src.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioUpdate,
)
from backend.src.services.usuario_service import UsuarioService
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from frontend.src.views.pages.usuario.usuario_alterar_senha import UsuarioAlterarSenhaPage
from frontend.src.views.pages.usuario.usuario_setores import UsuarioSetoresPage


class UsuarioPage:
    def __init__(self):
        self.USUARIO_VIEW_ATUAL = "usuario_view_atual"
        self.EDITANDO_USUARIO = "editando_usuario"
        self.SENHA_DESATIVADA = "senha_desativada"
        self.message = MensagemComponent(key_prefix="usuario")
        self.options_tipo = [tipo.value for tipo in TipoUsuario]

        if self.USUARIO_VIEW_ATUAL not in st.session_state:
            st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"

        if self.EDITANDO_USUARIO not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO] = None

        if self.SENHA_DESATIVADA not in st.session_state:
            st.session_state[self.SENHA_DESATIVADA] = False

    def renderizar(self):
        self.message.exibir_mensagem()

        view_atual = st.session_state.get(self.USUARIO_VIEW_ATUAL)
        dados_usuario = st.session_state.get(self.EDITANDO_USUARIO)
        usuario_id = None
        usuario_nome = ""

        if dados_usuario:
            usuario_id = dados_usuario["dados"].id
            usuario_nome = dados_usuario["dados"].nome

        match view_atual:
            case "cadastro":
                self.cadastro_view()
            case "lista":
                self.lista_view()
            case "alterar_senha":
                UsuarioAlterarSenhaPage(
                    usuario_id=usuario_id, usuario_nome=usuario_nome
                ).renderizar()
            case "setores":
                UsuarioSetoresPage(
                    usuario_id=usuario_id, usuario_nome=usuario_nome
                ).renderizar()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_USUARIO)
        is_edicao = editando is not None

        # 1. CARGA DE VALORES PADRÃO PARA OS INPUTS
        if is_edicao:
            usuario_dados = editando.get("dados")

            if hasattr(usuario_dados, "id"):
                id_padrao = usuario_dados.id
                codigo_padrao = str(getattr(usuario_dados, "codigo", "") or "")
                nome_padrao = getattr(usuario_dados, "nome", "")
                email_padrao = getattr(usuario_dados, "email", "")
                val_tipo = getattr(usuario_dados, "tipo_usuario")
                tipo_usuario_padrao = val_tipo.value if hasattr(val_tipo, "value") else str(val_tipo)
                ativo_padrao = getattr(usuario_dados, "ativo", True)
            elif isinstance(usuario_dados, dict):
                id_padrao = usuario_dados.get("id") or usuario_dados.get("ID")
                codigo_padrao = str(usuario_dados.get("codigo") or usuario_dados.get("Codigo") or "")
                nome_padrao = usuario_dados.get("nome") or usuario_dados.get("Nome") or ""
                email_padrao = usuario_dados.get("email") or usuario_dados.get("Email") or ""
                val_tipo = usuario_dados.get("tipo_usuario") or usuario_dados.get("Tipo usuario")
                tipo_usuario_padrao = val_tipo.value if hasattr(val_tipo, "value") else str(val_tipo)
                ativo_padrao = usuario_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            codigo_padrao = ""
            nome_padrao = ""
            email_padrao = ""
            tipo_usuario_padrao = self.options_tipo[0]
            ativo_padrao = True

        titulo_pagina = (
            f"Editando usuário: {nome_padrao}"
            if is_edicao
            else "Cadastrar usuário"
        )

        TitlePages(
            title_page=titulo_pagina,
            btn_nome="Lista de usuários",
            acao_btn=self.mudar_tela,
            parametro_acao="lista",
        ).title()

        # 2. ESTRUTURA DO FORMULÁRIO PRINCIPAL
        # Nota: removidas as 'key' explícitas que causavam conflito no reset
        with st.form(key="form_cadastro_usuario", clear_on_submit=not is_edicao):
            col_codigo, col_nome, col_email = st.columns([2, 4, 4])
            with col_codigo:
                codigo = st.text_input(
                    label="Código",
                    value=codigo_padrao,
                    placeholder="Automático se vazio...",
                )
            with col_nome:
                nome = st.text_input(
                    label="Nome",
                    value=nome_padrao,
                    placeholder="Informe o nome...",
                )
            with col_email:
                email = st.text_input(
                    label="Email",
                    value=email_padrao,
                    type="email",
                    placeholder="email@empresa.com",
                )

            col_tipo_usuario, col_senha, col_conf_senha = st.columns([2, 4, 4])
            with col_tipo_usuario:
                idx_tipo = self.options_tipo.index(tipo_usuario_padrao) if tipo_usuario_padrao in self.options_tipo else 0
                tipo_usuario = st.selectbox(
                    label="Tipo usuário",
                    options=self.options_tipo,
                    index=idx_tipo,
                )
            with col_senha:
                senha = st.text_input(
                    label="Senha",
                    type="password",
                    disabled=is_edicao,
                    placeholder="5 números..." if not is_edicao else "Usar botão alterar senha",
                )
            with col_conf_senha:
                conf_senha = st.text_input(
                    label="Confirmar senha",
                    type="password",
                    disabled=is_edicao,
                )

            ativo = st.checkbox(
                label="Ativo",
                disabled=not is_edicao,
                value=ativo_padrao,
            )

            Divider(color="gray").divider()

            btn_label = "Editar usuário" if is_edicao else "Cadastrar usuário"
            btn_cadastrar_alterar = st.form_submit_button(
                label=btn_label, type="primary"
            )

        # 3. AÇÕES SECUNDÁRIAS FORA DO FORM
        if is_edicao:
            col_btn_novo, col_btn_alterar_senha, col_btn_setores = st.columns(3)
            with col_btn_novo:
                st.button(
                    label="Novo",
                    width="stretch",
                    on_click=self.limpar_dados,
                )
            with col_btn_alterar_senha:
                if st.button("Alterar senha", width="stretch"):
                    st.session_state[self.USUARIO_VIEW_ATUAL] = "alterar_senha"
                    st.rerun()
            with col_btn_setores:
                if st.button("Setor(es) sob responsabilidade", width="stretch"):
                    st.session_state[self.USUARIO_VIEW_ATUAL] = "setores"
                    st.rerun()

        # 4. PROCESSAMENTO DO SUBMIT
        if btn_cadastrar_alterar:
            codigo_str = (codigo or "").strip()
            nome_str = (nome or "").strip()
            email_str = (email or "").strip()
            senha_str = (senha or "").strip()
            conf_senha_str = (conf_senha or "").strip()

            try:
                codigo_final = int(codigo_str) if codigo_str.isdigit() else None
                tipo_enum = TipoUsuario(tipo_usuario)

                if is_edicao:
                    dados_usuario = UsuarioUpdate(
                        id=id_padrao,
                        codigo=codigo_final,
                        nome=nome_str,
                        email=email_str,
                        tipo_usuario=tipo_enum,
                        ativo=ativo,
                    )
                    self.alterar_dados(usuario_id=id_padrao, dados_usuario=dados_usuario)
                else:
                    if self.validacao_senha(senha=senha_str, conf_senha=conf_senha_str):
                        dados_usuario = UsuarioCreate(
                            codigo=codigo_final,
                            nome=nome_str,
                            email=email_str,
                            tipo_usuario=tipo_enum,
                            senha=senha_str,
                            ativo=ativo,
                        )
                        self.salvar_dados(dados_usuario=dados_usuario)

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

    def validacao_senha(self, senha: str, conf_senha: str) -> bool:
        if not senha:
            self.message.definir_mensagem("Senha não informada", tipo="error")
            return False
        if len(senha) != 5:
            self.message.definir_mensagem(
                "A senha deve conter exatamente 5 caracteres!", tipo="error"
            )
            return False
        if not conf_senha:
            self.message.definir_mensagem(
                "Confirmação da senha não informada", tipo="error"
            )
            return False
        if senha != conf_senha:
            self.message.definir_mensagem(
                "As senhas não correspondem", tipo="error"
            )
            return False
        return True

    def lista_view(self):
        TitlePages(
            title_page="Lista de usuários",
            btn_nome="Cadastrar usuário",
            acao_btn=self.mudar_tela,
            parametro_acao="cadastro",
        ).title()

        usuarios = self.obter_todos_usuarios()

        if usuarios:
            dados_usuarios = [
                {
                    "ID": user.id,
                    "Codigo": user.codigo,
                    "Nome": user.nome,
                    "Email": user.email,
                    "Tipo usuario": user.tipo_usuario,
                    "Ativo": "Ativo" if user.ativo else "Inativo",
                }
                for user in usuarios
            ]
            evento_selecao = st.dataframe(
                data=dados_usuarios,
                width="stretch",
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
            )

            linha_selecionada = evento_selecao.get("selection", {}).get(
                "rows", []
            )

            if linha_selecionada:
                indice = linha_selecionada[0]
                usuario_selecionado = usuarios[indice]

                st.session_state[self.EDITANDO_USUARIO] = {
                    "indice": indice,
                    "dados": usuario_selecionado,
                }

                st.session_state[self.USUARIO_VIEW_ATUAL] = "cadastro"
                st.session_state[self.SENHA_DESATIVADA] = True
                st.rerun()
        else:
            st.write(" ### Não há usuários cadastrados!")

    def salvar_dados(self, dados_usuario: UsuarioCreate):
        try:
            with get_db() as db:
                novo_usuario = UsuarioService.criar_usuario(
                    db=db, usuario_dados=dados_usuario
                )
                self.message.definir_mensagem(
                    f"O usuário {novo_usuario.nome} foi cadastrado com sucesso!",
                    tipo="success",
                )
                self.resetar_contexto_edicao()
                st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"
                st.rerun()
        except Exception as e:
            self.message.definir_mensagem(str(e), tipo="error")

    def alterar_dados(self, usuario_id: int, dados_usuario: UsuarioUpdate):
        try:
            with get_db() as db:
                usuario_atualizado = UsuarioService.alterar_usuario(
                    db=db, usuario_id=usuario_id, usuario_dados=dados_usuario
                )
                self.message.definir_mensagem(
                    f"O usuário {usuario_atualizado.nome} foi alterado com sucesso!",
                    tipo="success",
                )
                self.resetar_contexto_edicao()
                st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"
                st.rerun()
        except Exception as e:
            self.message.definir_mensagem(str(e), tipo="error")

    def obter_todos_usuarios(self):
        try:
            with get_db() as db:
                return UsuarioService.obter_todos_usuarios(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar usuários: {str(e)}", tipo="error"
            )
            return []

    def mudar_tela(self, view: str):
        st.session_state[self.USUARIO_VIEW_ATUAL] = view
        self.resetar_contexto_edicao()
        st.rerun()

    def resetar_contexto_edicao(self):
        """Apenas limpa o estado de edição sem tentar modificar keys de widgets ativos."""
        st.session_state[self.EDITANDO_USUARIO] = None
        st.session_state[self.SENHA_DESATIVADA] = False

    def limpar_dados(self):
        """Função chamada exclusivamente via on_click antes dos widgets nascerem."""
        self.resetar_contexto_edicao()