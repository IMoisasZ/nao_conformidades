"""Módulo da Página de Setores (Frontend Streamlit)."""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.schemas.setor_schema import SetorCreate, SetorUpdate
from backend.src.services.setor_service import SetorService
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.title_page import TitlePages


class SetorPage:
    def __init__(self):
        self.CADASTRO_SETOR = "cadastro_setor"
        self.EDITANDO_SETOR = "editando_setor"
        self.message = MensagemComponent()

        if self.CADASTRO_SETOR not in st.session_state:
            st.session_state[self.CADASTRO_SETOR] = False

        if self.EDITANDO_SETOR not in st.session_state:
            st.session_state[self.EDITANDO_SETOR] = None

    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_SETOR]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_SETOR)
        is_edicao = editando is not None

        if is_edicao:
            setor_dados = editando.get("dados")

            if hasattr(setor_dados, "id"):
                id_padrao = setor_dados.id
                nome_padrao = getattr(setor_dados, "nome_setor", "") or ""
                ativo_padrao = getattr(setor_dados, "ativo", True)
            elif isinstance(setor_dados, dict):
                id_padrao = setor_dados.get("id") or setor_dados.get("ID")
                nome_padrao = (
                    setor_dados.get("nome_setor")
                    or setor_dados.get("Setor")
                    or ""
                )
                ativo_padrao = setor_dados.get("ativo", True)
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
            f"Editar setor: {nome_padrao}"
            if is_edicao
            else "Cadastrar setor"
        )
        TitlePages(
            title_page=titulo_pagina,
            btn_nome="Lista de setores",
            acao_btn=self.mudar_tela,
            parametro_acao=False,
        ).title()

        # Formulário que congela os valores dos campos até a submissão
        with st.form(key="form_cadastro_setor", clear_on_submit=not is_edicao):
            setor_col, ativo_col, espaco = st.columns(
                [4, 2, 4], vertical_alignment="bottom"
            )
            with setor_col:
                setor = st.text_input(
                    label="Setor",
                    value=nome_padrao,
                    placeholder="Informe o nome do setor...",
                )
            with ativo_col:
                ativo = st.checkbox(
                    label="Ativo",
                    value=ativo_padrao,
                    disabled=not is_edicao,
                )

            Divider(color="gray").divider()

            btn_label = "Editar setor" if is_edicao else "Cadastrar setor"
            btn_cadastrar_alterar = st.form_submit_button(
                label=btn_label, type="primary"
            )

        if is_edicao:
            st.button(
                label="Novo",
                width="stretch",
                on_click=self.limpar_dados,
            )

        if btn_cadastrar_alterar:
            nome_str = (setor or "").strip()

            try:
                if is_edicao:
                    dados_setor = SetorUpdate(
                        id=id_padrao, nome_setor=nome_str, ativo=ativo
                    )
                    self.alterar_dados(
                        setor_id=id_padrao, dados_setor=dados_setor
                    )
                else:
                    dados_setor = SetorCreate(
                        nome_setor=nome_str, ativo=ativo
                    )
                    self.salvar_dados(dados_setor=dados_setor)
            except (ValueError, ValidationError) as e:
                msg_erro = (
                    e.errors()[0]["msg"]
                    if isinstance(e, ValidationError)
                    else str(e)
                )
                self.message.definir_mensagem(
                    f"Erro ao cadastrar/alterar: {msg_erro}", tipo="error"
                )

    def lista_view(self):
        TitlePages(
            title_page="Lista de setores",
            btn_nome="Cadastrar setor",
            acao_btn=self.mudar_tela,
            parametro_acao=True,
        ).title()

        setores = self.obter_todos_setores()

        if setores:
            tabela_setores = [
                {
                    "ID": set_obj.id,
                    "Setor": set_obj.nome_setor,
                    "Ativo": "Ativo" if set_obj.ativo else "Inativo",
                }
                for set_obj in setores
            ]

            evento_selecao = st.dataframe(
                data=tabela_setores,
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
                setor_selecionado = setores[indice]

                st.session_state[self.EDITANDO_SETOR] = {
                    "indice": indice,
                    "dados": setor_selecionado,
                }

                st.session_state[self.CADASTRO_SETOR] = True
                st.rerun()
        else:
            st.write(" ### Não há setores cadastrados!")

    def salvar_dados(self, dados_setor: SetorCreate):
        try:
            with get_db() as db:
                novo_setor = SetorService.criar_setor(
                    db=db, setor_dados=dados_setor
                )
                self.message.definir_mensagem(
                    f"O setor {novo_setor.nome_setor} foi cadastrado com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_SETOR] = False
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

    def alterar_dados(self, setor_id: int, dados_setor: SetorUpdate):
        try:
            with get_db() as db:
                setor_atualizado = SetorService.alterar_setor(
                    db=db, setor_id=setor_id, setor_dados=dados_setor
                )
                self.message.definir_mensagem(
                    f"O setor {setor_atualizado.nome_setor} foi atualizado com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_SETOR] = False
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

    def obter_todos_setores(self):
        try:
            with get_db() as db:
                return SetorService.obter_todos_setores(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar setores: {str(e)}", tipo="error"
            )
            return []

    def mudar_tela(self, status: bool = False):
        st.session_state[self.CADASTRO_SETOR] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        """Reseta apenas os dados de edição sem modificar chaves ativas dos widgets."""
        st.session_state[self.EDITANDO_SETOR] = None
        st.session_state.pop("setor_carregado_id", None)