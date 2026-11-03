"""Módulo de Interface Gráfica para Gestão de Códigos de Não Conformidade.

Este módulo contém a classe `CodigoNCPage`, responsável por gerenciar a view em Streamlit
para listagem, cadastro e edição dos códigos de não conformidade do sistema.
"""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.models.codigo_nc_model import TipoNC
from backend.src.schemas.codigo_nc_schema import CodigoNCCreate, CodigoNCUpdate
from backend.src.services.codigo_nc_service import CodigoNCService
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.title_page import TitlePages


class CodigoNCPage:
    """Classe responsável por renderizar as telas de cadastro e listagem de Códigos de NC.

    Gerencia o estado da sessão (`st.session_state`), alternando entre a visualização
    em tabela e o formulário de cadastro/edição, integrando as chamadas ao `CodigoNCService`.
    """

    def __init__(self):
        """Inicializa as chaves de sessão, o componente de mensagem e as opções de tipo."""
        self.CADASTRO_CODGO_NC = "cadastro_codigo_nc"
        self.EDITANDO_CODIGO_NC = "editando_codigo_nc"
        self.message = MensagemComponent(key_prefix="codigo_nc")
        self.options_tipo = [tipo.value for tipo in TipoNC]

        if self.CADASTRO_CODGO_NC not in st.session_state:
            st.session_state[self.CADASTRO_CODGO_NC] = False

        if self.EDITANDO_CODIGO_NC not in st.session_state:
            st.session_state[self.EDITANDO_CODIGO_NC] = None

    def renderizar(self):
        """Orquestra a exibição de mensagens de feedback e renderiza a view atual (lista ou formulário)."""
        self.message.exibir_mensagem()
        if st.session_state.get(self.CADASTRO_CODGO_NC):
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        """Renderiza o formulário de inclusão e edição de código de não conformidade."""
        editando = st.session_state.get(self.EDITANDO_CODIGO_NC)
        is_edicao = editando is not None

        if is_edicao:
            dados_codigo_nc = editando.get("dados")

            if hasattr(dados_codigo_nc, "id"):
                id_padrao = dados_codigo_nc.id
                descricao_padrao = getattr(dados_codigo_nc, "descricao", "")
                val_tipo = getattr(dados_codigo_nc, "tipo")
                tipo_padrao = (
                    val_tipo.value
                    if hasattr(val_tipo, "value")
                    else str(val_tipo)
                )
                ativo_padrao = getattr(dados_codigo_nc, "ativo", True)
            elif isinstance(dados_codigo_nc, dict):
                id_padrao = dados_codigo_nc.get("id") or dados_codigo_nc.get(
                    "ID"
                )
                descricao_padrao = (
                    dados_codigo_nc.get("descricao")
                    or dados_codigo_nc.get("Descricao")
                    or dados_codigo_nc.get("Descrição")
                    or ""
                )
                val_tipo = (
                    dados_codigo_nc.get("tipo")
                    or dados_codigo_nc.get("Tipo")
                    or ""
                )
                tipo_padrao = (
                    val_tipo.value
                    if hasattr(val_tipo, "value")
                    else str(val_tipo)
                )
                ativo_padrao = dados_codigo_nc.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            descricao_padrao = ""
            tipo_padrao = self.options_tipo[0]
            ativo_padrao = True

        titulo_pagina = (
            f"Editando código: {id_padrao} - Descrição: {descricao_padrao}"
            if is_edicao
            else "Cadastro código não conformidade"
        )
        TitlePages(
            title_page=titulo_pagina,
            btn_nome="Lista de código NC",
            acao_btn=self.mudar_tela,
            parametro_acao=False,
            tamanho_cols=[8, 1, 2],
        ).title()

        with st.form(
            key="form_cadastro_codigo_nc", clear_on_submit=not is_edicao
        ):
            col_descricao, col_tipo, col_ativo = st.columns(
                [16, 4, 1], vertical_alignment="bottom"
            )

            with col_descricao:
                descricao = st.text_input(
                    label="Descrição",
                    placeholder="Informe a descrição NC",
                    value=descricao_padrao,
                )
            with col_tipo:
                idx_tipo = (
                    self.options_tipo.index(tipo_padrao)
                    if tipo_padrao in self.options_tipo
                    else 0
                )
                tipo = st.selectbox(
                    label="Tipo", options=self.options_tipo, index=idx_tipo
                )
            with col_ativo:
                ativo = st.checkbox(
                    label="Ativo",
                    disabled=False if is_edicao else True,
                    value=ativo_padrao,
                )

            Divider(color="gray").divider()

            btn_label = (
                "Editar código NC" if is_edicao else "Cadastrar código NC"
            )
            btn_cadastrar_alterar = st.form_submit_button(
                label=btn_label, type="primary", width="content"
            )

        if is_edicao:
            st.button(
                label="Novo", width="stretch", on_click=self.limpar_dados
            )

        if btn_cadastrar_alterar:
            try:
                descricao_str = (descricao or "").strip()
                tipo_enum = TipoNC(tipo)

                if is_edicao:
                    dados_codigo_nc = CodigoNCUpdate(
                        id=id_padrao,
                        descricao=descricao_str,
                        tipo=tipo_enum,
                        ativo=ativo,
                    )
                    self.alterar_dados(
                        codigo_nc_id=id_padrao, dados_codigo_nc=dados_codigo_nc
                    )
                else:
                    dados_codigo_nc = CodigoNCCreate(
                        descricao=descricao_str, tipo=tipo_enum, ativo=ativo
                    )
                    self.salvar_dados(dados_codigo_nc=dados_codigo_nc)
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

    def lista_view(self):
        """Renderiza a tabela de listagem dos códigos de não conformidade cadastrados."""
        TitlePages(
            title_page="Lista de códigos não conformidade",
            btn_nome="Cadastro de código NC",
            acao_btn=self.mudar_tela,
            parametro_acao=True,
            tamanho_cols=[8, 1, 2],
        ).title()

        codigos_nc = self.obter_todos_codigos_nc()

        if codigos_nc:
            tabela_codigo_nc = [
                {
                    "ID": cod_nc.id,
                    "Descrição": cod_nc.descricao,
                    "Tipo": (
                        cod_nc.tipo.value
                        if hasattr(cod_nc.tipo, "value")
                        else str(cod_nc.tipo)
                    ),
                    "Ativo": "Ativo" if cod_nc.ativo else "Inativo",
                }
                for cod_nc in codigos_nc
            ]

            evento_selecao = st.dataframe(
                data=tabela_codigo_nc,
                on_select="rerun",
                hide_index=True,
                selection_mode="single-row",
            )

            linha_selecionada = evento_selecao.get("selection", {}).get(
                "rows", []
            )

            if linha_selecionada:
                indice = linha_selecionada[0]
                codigo_nc_selecionado = codigos_nc[indice]

                st.session_state[self.EDITANDO_CODIGO_NC] = {
                    "indice": indice,
                    "dados": codigo_nc_selecionado,
                }
                st.session_state[self.CADASTRO_CODGO_NC] = True
                st.rerun()
        else:
            st.write("### Não há códigos de não conformidade cadastrados!")

    def salvar_dados(self, dados_codigo_nc: CodigoNCCreate):
        """Persiste um novo código de NC no banco de dados.

        Args:
            dados_codigo_nc (CodigoNCCreate): DTO com os dados validados do formulário.
        """
        try:
            with get_db() as db:
                novo_codigo_nc = CodigoNCService.criar_codigo_nc(
                    db=db, dados_codigo_nc=dados_codigo_nc
                )
                self.message.definir_mensagem(
                    f"Código NC '{novo_codigo_nc.descricao}' cadastrado com sucesso!",
                    tipo="success",
                )
                self.mudar_tela(status=False)
        except Exception as e:
            self.message.definir_mensagem(str(e), tipo="error")

    def alterar_dados(self, codigo_nc_id: int, dados_codigo_nc: CodigoNCUpdate):
        """Atualiza os dados de um código de NC existente no banco de dados.

        Args:
            codigo_nc_id (int): ID do registro a ser atualizado.
            dados_codigo_nc (CodigoNCUpdate): DTO contendo as alterações.
        """
        try:
            with get_db() as db:
                codigo_nc_atualizado = CodigoNCService.alterar_codigo_nc(
                    db=db,
                    codigo_nc_id=codigo_nc_id,
                    dados_codigo_nc=dados_codigo_nc,
                )
                self.message.definir_mensagem(
                    f"O código NC '{codigo_nc_atualizado.descricao}' foi alterado com sucesso!",
                    tipo="success",
                )
                self.mudar_tela(status=False)
        except Exception as e:
            self.message.definir_mensagem(str(e), tipo="error")

    def obter_todos_codigos_nc(self):
        """Busca a lista de todos os códigos de NC cadastrados via serviço.

        Returns:
            list: Lista de objetos de resposta contendo os códigos de NC.
        """
        try:
            with get_db() as db:
                codigos_nc = CodigoNCService.obter_todos_codigos_nc(db=db)
                return codigos_nc
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar códigos de não conformidade: {str(e)}",
                tipo="error",
            )
            return []

    def limpar_dados(self):
        """Reseta o estado de edição da sessão."""
        st.session_state[self.EDITANDO_CODIGO_NC] = None
        st.session_state.pop("codigo_nc_carregado_id", None)

    def mudar_tela(self, status: bool):
        """Alterna a visualização entre o formulário de cadastro/edição e a listagem.

        Args:
            status (bool): True para exibir o cadastro, False para exibir a lista.
        """
        self.limpar_dados()
        st.session_state[self.CADASTRO_CODGO_NC] = status
        st.rerun()
        