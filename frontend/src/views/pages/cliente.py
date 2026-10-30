import streamlit as st
from pydantic import ValidationError

from components.title_page import TitlePages
from components.input import InputComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider
from components.mensagem import MensagemComponent

from backend.src.connection.db_connection import get_db
from backend.src.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from backend.src.services.cliente_service import ClienteService

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

            # Garante a leitura do ID tanto se for Objeto (Pydantic/Model) quanto Dicionário
            if hasattr(cliente_dados, "id"):
                id_padrao = cliente_dados.id
                nome_padrao = getattr(cliente_dados, "nome_cliente", "")
                ativo_padrao = getattr(cliente_dados, "ativo", True)
            elif isinstance(cliente_dados, dict):
                id_padrao = cliente_dados.get("id")
                nome_padrao = cliente_dados.get("nome_cliente") or cliente_dados.get("Cliente") or ""
                ativo_padrao = cliente_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            if "input_cliente" not in st.session_state:
                st.session_state["input_cliente"] = ""
            if "checkbox_ativo" not in st.session_state:
                st.session_state["checkbox_ativo"] = True

        titulo_pagina = f"Editar cliente: {nome_padrao}" if is_edicao else "Cadastrar cliente"
        TitlePages(title_page=titulo_pagina, btn_nome="Lista de clientes", acao_btn=self.mudar_tela, parametro_acao=False).title()

        if id_padrao and st.session_state.get("cliente_carregado_id") != id_padrao:
            st.session_state["input_cliente"] = nome_padrao
            st.session_state["checkbox_ativo"] = ativo_padrao
            st.session_state["cliente_carregado_id"] = id_padrao

        cliente_col, ativo_col, espaco = st.columns([4,2,4], vertical_alignment="bottom")
        with cliente_col:
            cliente = InputComponent(label="Cliente", key="input_cliente", placeholder="Informe o nome do cliente...").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", key="checkbox_ativo", disabled=False if is_edicao else True, value=st.session_state.get("checkbox_ativo", True)).checkbox()

        Divider(color="gray").divider()

        btn_incluir_col, btn_novo_col = st.columns(2)
        with btn_incluir_col:
            btn_cadastro_alteracao = ButtonComponent(label="Editar cliente" if is_edicao else "Cadastrar cliente", key="btn_cadastrar_cliente").btn()
        with btn_novo_col:
            btn_novo = ButtonComponent(label="Novo", key="btn_novo_cliente", onclick=self.acao_botao_novo).btn()

        if btn_cadastro_alteracao:
            try:
                nome_str = (cliente or "").strip()
                if is_edicao:
                    dados_cliente = ClienteUpdate(id=id_padrao, nome_cliente=nome_str, ativo=ativo)
                    self.alterar_dados(cliente_id=id_padrao, dados_cliente=dados_cliente)
                else:
                    dados_cliente = ClienteCreate(nome_cliente=nome_str, ativo=ativo)
                    self.salvar_dados(dados_cliente=dados_cliente)
            except (ValueError, ValidationError) as e:
                msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
                self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
                st.rerun()

    def lista_view(self):
        TitlePages(title_page="Lista de clientes", btn_nome="Cadastrar cliente", acao_btn=self.mudar_tela, parametro_acao=True).title()

        clientes = self.obter_todos_clientes()

        if clientes:
            dados_cliente = [
                {
                    "ID": cli.id,
                    "Cliente": cli.nome_cliente,
                    "Ativo": "Ativo" if cli.ativo else "Inativo"
                }
                for cli in clientes
            ]
            evento_selecao = st.dataframe(data=dados_cliente, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")
            
            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])
    
            if linha_selecionada:
                indice = linha_selecionada[0]
                cliente_selecionado = clientes[indice]
    
                st.session_state[self.EDITANDO_CLIENTE] = {
                    "indice": indice,
                    "dados": cliente_selecionado
                }
    
                st.session_state[self.CADASTRO_CLIENTE] = True
                st.rerun()
        else:
            st.write(" #### Não há clientes cadastrados!")
        
    def salvar_dados(self, dados_cliente:ClienteCreate):
        try:
            with get_db() as db:
                novo_cliente = ClienteService.criar_cliente(db=db, cliente_dados=dados_cliente)
                self.message.definir_mensagem(f"O cliente {novo_cliente.nome_cliente} foi cadastrado com sucesso!", tipo="success")
                # Reseta controle de tela e força rerender limpo
                st.session_state[self.EDITANDO_CLIENTE] = None
                st.session_state["cliente_carregado_id"] = None
                st.session_state[self.CADASTRO_CLIENTE] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()

    def alterar_dados(self, cliente_id:int, dados_cliente:ClienteUpdate):
        try:
            with get_db() as db:
                cliente_alterado = ClienteService.alterar_cliente(db=db, cliente_id=cliente_id, cliente_dados=dados_cliente)
                self.message.definir_mensagem(f"O cliente {cliente_alterado.nome_cliente} foi atualizado com sucesso!", tipo="success")
                st.session_state[self.EDITANDO_CLIENTE] = None
                st.session_state["cliente_carregado_id"] = None
                st.session_state[self.CADASTRO_CLIENTE] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao alterar: {msg_erro}", tipo="error")
            st.rerun()

    def obter_todos_clientes(self):
        try:
            with get_db() as db:
                clientes = ClienteService.obter_todos_clientes(db=db)
                return clientes
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar clientes: {str(e)}", tipo="error")
            return []

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_CLIENTE] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        st.session_state[self.EDITANDO_CLIENTE] = None
        st.session_state["cliente_carregado_id"] = None

        st.session_state["input_cliente"] = ""
        st.session_state["checkbox_ativo"] = True

    def acao_botao_novo(self):
        self.limpar_dados()
        st.rerun()

