import streamlit as st
from pydantic import ValidationError

from components.title_page import TitlePages
from components.input import InputComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider
from components.mensagem import MensagemComponent

from backend.src.connection.db_connection import get_db
from backend.src.schemas.fornecedor_schema import FornecedorUpdate, FornecedorCreate
from backend.src.services.fornecedor_service import FornecedorService

class FornecedorPage:
    def __init__(self):
        self.CADASTRO_FORNECEDOR = "cadastro_fornecedor"
        self.EDITANDO_FORNECEDOR = "editando_fornecedor"
        self.message = MensagemComponent(key_prefix="fornecedor")

        if self.CADASTRO_FORNECEDOR not in st.session_state:
            st.session_state[self.CADASTRO_FORNECEDOR] = False

        if self.EDITANDO_FORNECEDOR not in st.session_state:
            st.session_state[self.EDITANDO_FORNECEDOR] = None

    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_FORNECEDOR]:
            self.cadastro_view()
        else:
            self.lista_view()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_FORNECEDOR)
        is_edicao = editando is not None

        if is_edicao:
            fornecedor_dados = editando.get("dados")

            if hasattr(fornecedor_dados, "id"):
                id_padrao = fornecedor_dados.id
                nome_padrao = getattr(fornecedor_dados, "nome_fornecedor", "")
                ativo_padrao = getattr(fornecedor_dados, "ativo", True)
            elif isinstance(fornecedor_dados, dict):
                id_padrao = fornecedor_dados.get("id")
                nome_padrao = fornecedor_dados.get("nome_fornecedor") or fornecedor_dados.get("Fornecedor") or ""
                ativo_padrao = fornecedor_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            if "input_fornecedor" not in st.session_state:
                st.session_state["input_fornecedor"] = ""

            if "checkbox_ativo" not in st.session_state:
                st.session_state["checkbox_ativo"] = True

        titulo_pagina = f"Editar fornecedor: {nome_padrao}" if is_edicao else "Cadastrar fornecedor"
        TitlePages(title_page=titulo_pagina,btn_nome="Lista de fornecedores", acao_btn=self.mudar_tela, parametro_acao=False).title()

        if id_padrao and st.session_state.get("fornecedor_carregado_id") != id_padrao:
            st.session_state["input_fornecedor"] = nome_padrao
            st.session_state["checkbox_ativo"] = ativo_padrao
            st.session_state["fornecedor_carregado_id"] = id_padrao

        fornecedor_col, ativo_col, espaco = st.columns([4,2,4], vertical_alignment="bottom")
        with fornecedor_col:
            fornecedor = InputComponent(label="Fornecedor", key="input_fornecedor").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", key="checkbox_ativo", disabled=False if is_edicao else True, value=st.session_state.get("checkbox_ativo", True)).checkbox()

        Divider(color="gray").divider()

        btn_cadastrar_col, btn_novo_col = st.columns(2)
        with btn_cadastrar_col:
            btn_cadastro_alteracao = ButtonComponent(label="Editar fornecedor" if is_edicao else "Cadastrar fornecedor", key="btn_cadastrar_editar_fornecedor").btn()
        with btn_novo_col:
            ButtonComponent(label="Novo", key="btn_novo_fornecedor", onclick=self.acao_botao_novo).btn()

        if btn_cadastro_alteracao:
            try:
                nome_str = (fornecedor or "").strip()
                if is_edicao:
                    dados_fornecedor = FornecedorUpdate(id=id_padrao, nome_fornecedor=nome_str, ativo=ativo)
                    self.alterar_dados(fornecedor_id=id_padrao, fornecedor_dados=dados_fornecedor)
                else:
                    dados_fornecedor = FornecedorCreate(nome_fornecedor=nome_str, ativo=ativo)
                    self.salvar_dados(fornecedor_dados=dados_fornecedor)
            except (ValueError, ValidationError) as e:
                            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
                            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
                            st.rerun()

    def lista_view(self):
        TitlePages(title_page="Lista de fornecedores",btn_nome="Cadastrar fornecedor", acao_btn=self.mudar_tela, parametro_acao=True).title()

        fornecedores = self.obter_todos_fornecedores()

        if fornecedores:
            dados_fornecedor = [
                {
                    "ID": forn.id,
                    "Fornecedor": forn.nome_fornecedor,
                    "Ativo": "Ativo" if forn.ativo else "Inativo"
                }
                for forn in fornecedores
            ]

            evento_selecao = st.dataframe(data=dados_fornecedor, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")

            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])

            if linha_selecionada:
                indice = linha_selecionada[0]
                fornecedor_selecionado = fornecedores[indice]

                st.session_state[self.EDITANDO_FORNECEDOR] = {
                    "indice": indice,
                    "dados": fornecedor_selecionado
                }

                st.session_state[self.CADASTRO_FORNECEDOR] = True
                st.rerun()
        else:
            st.write(" ### Não há fornecedores cadastrados!")
    
    def salvar_dados(self, fornecedor_dados:FornecedorCreate):
        try:
            with get_db() as db:
                novo_fornecedor = FornecedorService.criar_fornecedor(db=db, fornecedor_dados=fornecedor_dados)
                self.message.definir_mensagem(f"O fornecedor {novo_fornecedor.nome_fornecedor} foi cadastrado com sucesso!", tipo="success")
                st.session_state[self.EDITANDO_FORNECEDOR] = None
                st.session_state["fornecedor_carregado_id"] = None
                st.session_state[self.CADASTRO_FORNECEDOR] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()

    def alterar_dados(self, fornecedor_id:int, fornecedor_dados: FornecedorUpdate):
        try:
            with get_db() as db:
                fornecedor_atualizado = FornecedorService.alterar_fornecedor(db=db, fornecedor_id=fornecedor_id, fornecedor_dados=fornecedor_dados)
                self.message.definir_mensagem(f"O fornecedor {fornecedor_dados.nome_fornecedor} foi alterado com sucesso!", tipo="success")
                st.session_state[self.EDITANDO_FORNECEDOR] = None
                st.session_state["fornecedor_carregado_id"] = None
                st.session_state[self.CADASTRO_FORNECEDOR] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao alterar: {msg_erro}", tipo="error")
            st.rerun()

    def obter_todos_fornecedores(self):
        try:
            with get_db() as db:
                fornecedores = FornecedorService.obter_todos_fornecedores(db=db)
                return fornecedores
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar fornecedores: {str(e)}", tipo="error")
            return []

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_FORNECEDOR] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        st.session_state[self.EDITANDO_FORNECEDOR] = None
        st.session_state["fornecedor_carregado_id"] = None

        st.session_state["input_fornecedor"] = ""
        st.session_state["checkbox_ativo"] = True

    def acao_botao_novo(self):
        self.limpar_dados()
        st.rerun()