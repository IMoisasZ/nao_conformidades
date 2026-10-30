import streamlit as st
from pydantic import ValidationError

from components.input import InputComponent
from components.button import ButtonComponent
from components.checkbox import CheckboxComponent
from components.mensagem import MensagemComponent
from components.divider import Divider
from components.title_page import TitlePages

from backend.src.connection.db_connection import get_db
from backend.src.schemas.setor_schema import SetorCreate, SetorUpdate
from backend.src.services.setor_service import SetorService

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

            if hasattr(setor_dados,"id"):
                id_padrao = setor_dados.id
                nome_padrao = setor_dados.nome_setor
                ativo_padrao = setor_dados.ativo
            elif isinstance(setor_dados, dict):
                id_padrao = setor_dados.get("id") or setor_dados.get("ID")
                nome_padrao = setor_dados.get("nome_setor") or setor_dados.get("Setor") or ""
                ativo_padrao = setor_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
        else:
            id_padrao = None
            if "input_setor" not in st.session_state:
                st.session_state["input_setor"] = ""

            if "checkbox_ativo_setor" not in st.session_state:
                st.session_state["checkbox_ativo_setor"] = True

        titulo_pagina = f"Editar setor: {nome_padrao}" if is_edicao else "Cadastrar setor"                
        TitlePages(title_page=titulo_pagina, btn_nome="Lista de setores", acao_btn=self.mudar_tela, parametro_acao=False).title()

        if id_padrao and st.session_state.get("setor_carregado_id") != id_padrao:
            st.session_state["input_setor"] = nome_padrao
            st.session_state["checkbox_ativo_setor"] = ativo_padrao
            st.session_state["setor_carregado_id"] = id_padrao 

        setor_col, ativo_col, espaco = st.columns([4,2,4], vertical_alignment="bottom")
        with setor_col:
            setor = InputComponent(label="Setor", key="input_setor").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", disabled=False if is_edicao else True, value=st.session_state.get("checkbox_ativo_setor", True), key="checkbox_ativo_setor").checkbox()

        Divider(color="gray").divider()
        
        btn_cadastrar_col, btn_novo_col = st.columns(2)
        with btn_cadastrar_col:     
            btn_cadastrar_alterar = ButtonComponent(label="Editar setor" if is_edicao else "Cadastrar setor", key="btn_cadastrar_alterar").btn()
        with btn_novo_col:
            ButtonComponent(label="Novo", key="btn_novo_setor", onclick=self.acao_botao_novo).btn()

        if btn_cadastrar_alterar:
            try:
                nome_str = (setor or "").strip()
                if is_edicao:
                    dados_setor = SetorUpdate(id=id_padrao, nome_setor=nome_str, ativo=ativo)
                    self.alterar_dados(setor_id=id_padrao, dados_setor=dados_setor)
                else:
                    dados_setor = SetorCreate(nome_setor=nome_str, ativo=ativo)
                    self.salvar_dados(dados_setor=dados_setor)
            except (ValueError, ValidationError) as e:
                msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
                self.message.definir_mensagem(f"Erro ao cadastrar/alterar: {msg_erro}", tipo="error")
                st.rerun()        

    def lista_view(self):
        TitlePages(title_page="Lista de setores", btn_nome="Cadastrar setor", acao_btn=self.mudar_tela, parametro_acao=True).title()

        setores = self.obter_todos_setores()

        if setores:
            tabela_setores = [
                {
                    "ID": set.id,
                    "Setor": set.nome_setor,
                    "Ativo": "Ativo" if set.ativo else "Inativo"
                }
                for set in setores
            ]

            evento_selecao = st.dataframe(data=tabela_setores, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")

            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])

            if linha_selecionada:
                indice = linha_selecionada[0]
                setor_selecionado = setores[indice]

                st.session_state[self.EDITANDO_SETOR] = {
                    "indice": indice,
                    "dados": setor_selecionado
                }

                st.session_state[self.CADASTRO_SETOR] = True
                st.rerun()
        else:
            st.write(" ### Não há setores cadastrados!")
    
    def salvar_dados(self, dados_setor:SetorCreate):
        try:
            with get_db() as db:
                novo_setor = SetorService.criar_setor(db=db, setor_dados=dados_setor)
                self.message.definir_mensagem(f"O setor {novo_setor.nome_setor} foi cadastrado com sucesso!", tipo="success")
                st.session_state[self.EDITANDO_SETOR] = None
                st.session_state["setor_carregado_id"] = None
                st.session_state[self.CADASTRO_SETOR] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()

    def alterar_dados(self, setor_id:int, dados_setor: SetorUpdate):
        try:
            with get_db() as db:
                setor_atualizado = SetorService.alterar_setor(db=db, setor_id=setor_id, setor_dados=dados_setor)
                self.message.definir_mensagem(f"O setor {setor_atualizado.nome_setor} foi atualizado com sucesso!", tipo="success")
                st.session_state[self.EDITANDO_SETOR] = None
                st.session_state["setor_carregado_id"] = None
                st.session_state[self.CADASTRO_SETOR] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao alterar: {msg_erro}", tipo="error")
            st.rerun()

    def obter_todos_setores(self):
        try:
            with get_db() as db:
                setores = SetorService.obter_todos_setores(db=db)
                return setores
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar setores: {str(e)}", tipo="error")
            return []

    def mudar_tela(self, status:bool = None):
        st.session_state[self.CADASTRO_SETOR] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        st.session_state[self.EDITANDO_SETOR] = None
        st.session_state["setor_carregado_id"] = None

        st.session_state["input_setor"] = ""
        st.session_state["checkbox_ativo_setor"] = True

    def acao_botao_novo(self):
            self.limpar_dados()
            st.rerun()