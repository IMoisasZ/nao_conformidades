"""Módulo da Página de Clientes (Frontend Streamlit)."""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from backend.src.services.cliente_service import ClienteService
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.title_page import TitlePages


class ClientePage:
    def __init__(self):
        self.CADASTRO_CLIENTE = "cadastro_cliente"
        self.EDITANDO_CLIENTE = "editando_cliente"
        self.message = MensagemComponent(key_prefix="cliente")

        if self.CADASTRO_CLIENTE not in st.session_state:
            st.session_state[self.CADASTRO_CLIENTE] = False

        if self.EDITANDO_CLIENTE not in st.session_state:
            st.session_state[self.EDITANDO_CLIENTE] = None

    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_CLIENTE]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_CLIENTE)
        is_edicao = editando is not None

        if is_edicao:
            cliente_dados = editando.get("dados")

            if hasattr(cliente_dados, "id"):
                id_padrao = cliente_dados.id
                nome_padrao = getattr(cliente_dados, "nome_cliente", "") or ""
                ativo_padrao = getattr(cliente_dados, "ativo", True)
            elif isinstance(cliente_dados, dict):
                id_padrao = cliente_dados.get("id") or cliente_dados.get("ID")
                nome_padrao = (
                    cliente_dados.get("nome_cliente")
                    or cliente_dados.get("Cliente")
                    or ""
                )
                ativo_padrao = cliente_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
                nome_padrao = ""
                ativo_padrao = True
        else:
            id_padrao = None
            nome_padrao = ""
            ativo_padrao = True

        titulo_pagina = (
            f"Editar cliente: {nome_padrao}"
            if is_edicao
            else "Cadastrar cliente"
        )
        TitlePages(
            title_page=titulo_pagina,
            btn_nome="Lista de clientes",
            acao_btn=self.mudar_tela,
            parametro_acao=False,
        ).title()

        # Formulário que congela os valores dos campos até a submissão
        with st.form(key="form_cadastro_cliente", clear_on_submit=not is_edicao):
            cliente_col, ativo_col, espaco = st.columns(
                [4, 2, 4], vertical_alignment="bottom"
            )
            with cliente_col:
                cliente = st.text_input(
                    label="Cliente",
                    value=nome_padrao,
                    placeholder="Informe o nome do cliente...",
                )
            with ativo_col:
                ativo = st.checkbox(
                    label="Ativo",
                    value=ativo_padrao,
                    disabled=not is_edicao,
                )

            Divider(color="gray").divider()

            btn_label = "Editar cliente" if is_edicao else "Cadastrar cliente"
            btn_cadastro_alteracao = st.form_submit_button(
                label=btn_label, type="primary"
            )

        if is_edicao:
            st.button(
                label="Novo",
                width="stretch",
                on_click=self.limpar_dados,
            )

        if btn_cadastro_alteracao:
            nome_str = (cliente or "").strip()

            try:
                if is_edicao:
                    dados_cliente = ClienteUpdate(
                        id=id_padrao, nome_cliente=nome_str, ativo=ativo
                    )
                    self.alterar_dados(
                        cliente_id=id_padrao, dados_cliente=dados_cliente
                    )
                else:
                    dados_cliente = ClienteCreate(
                        nome_cliente=nome_str, ativo=ativo
                    )
                    self.salvar_dados(dados_cliente=dados_cliente)
            except (ValueError, ValidationError) as e:
                msg_erro = (
                    e.errors()[0]["msg"]
                    if isinstance(e, ValidationError)
                    else str(e)
                )
                self.message.definir_mensagem(
                    f"Erro ao cadastrar: {msg_erro}", tipo="error"
                )

    def lista_view(self):
        TitlePages(
            title_page="Lista de clientes",
            btn_nome="Cadastrar cliente",
            acao_btn=self.mudar_tela,
            parametro_acao=True,
        ).title()

        clientes = self.obter_todos_clientes()

        if clientes:
            dados_cliente = [
                {
                    "ID": cli.id,
                    "Cliente": cli.nome_cliente,
                    "Ativo": "Ativo" if cli.ativo else "Inativo",
                }
                for cli in clientes
            ]
            evento_selecao = st.dataframe(
                data=dados_cliente,
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
                cliente_selecionado = clientes[indice]

                st.session_state[self.EDITANDO_CLIENTE] = {
                    "indice": indice,
                    "dados": cliente_selecionado,
                }

                st.session_state[self.CADASTRO_CLIENTE] = True
                st.rerun()
        else:
            st.write(" #### Não há clientes cadastrados!")

    def salvar_dados(self, dados_cliente: ClienteCreate):
        try:
            with get_db() as db:
                novo_cliente = ClienteService.criar_cliente(
                    db=db, cliente_dados=dados_cliente
                )
                self.message.definir_mensagem(
                    f"O cliente {novo_cliente.nome_cliente} foi cadastrado com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_CLIENTE] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = (
                e.errors()[0]["msg"]
                if isinstance(e, ValidationError)
                else str(e)
            )
            self.message.definir_mensagem(
                f"Erro ao cadastrar: {msg_erro}", tipo="error"
            )

    def alterar_dados(self, cliente_id: int, dados_cliente: ClienteUpdate):
        try:
            with get_db() as db:
                cliente_alterado = ClienteService.alterar_cliente(
                    db=db, cliente_id=cliente_id, cliente_dados=dados_cliente
                )
                self.message.definir_mensagem(
                    f"O cliente {cliente_alterado.nome_cliente} foi atualizado com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_CLIENTE] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = (
                e.errors()[0]["msg"]
                if isinstance(e, ValidationError)
                else str(e)
            )
            self.message.definir_mensagem(
                f"Erro ao alterar: {msg_erro}", tipo="error"
            )

    def obter_todos_clientes(self):
        try:
            with get_db() as db:
                return ClienteService.obter_todos_clientes(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar clientes: {str(e)}", tipo="error"
            )
            return []

    def mudar_tela(self, status: bool):
        st.session_state[self.CADASTRO_CLIENTE] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        """Reseta apenas os dados de edição sem modificar chaves ativas dos widgets."""
        st.session_state[self.EDITANDO_CLIENTE] = None
        st.session_state.pop("cliente_carregado_id", None)