import streamlit as st
from pydantic import ValidationError

from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from components.divider import Divider

from backend.src.connection.db_connection import get_db
from backend.src.schemas.operacao_schema import OperacaoCreate, OperacaoUpdate
from backend.src.services.operacao_service import OperacaoService
class OperacaoPage:
    def __init__(self):
        self.CADASTRO_OPERACAO = "cadastro_operacao"
        self.EDITANDO_OPERACAO = "editando_operacao"
        self.message = MensagemComponent()
        
        if self.CADASTRO_OPERACAO not in st.session_state:
            st.session_state[self.CADASTRO_OPERACAO] = False
            
        if self.EDITANDO_OPERACAO not in st.session_state:
            st.session_state[self.EDITANDO_OPERACAO] = None
            
    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_OPERACAO]:
            self.cadastro_view()
        else:
            self.lista_view()
            
    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_OPERACAO)
        is_edicao = editando is not None
        
        if is_edicao:
            operacao_dados = editando.get("dados")
            
            if hasattr(operacao_dados, "id"):
                id_padrao = operacao_dados.id
                nome_padrao = getattr(operacao_dados, "nome_operacao", "") or ""
                ativo_padrao = getattr(operacao_dados, "ativo", True)
            elif isinstance(operacao_dados, dict):
                id_padrao = operacao_dados.get("id") or operacao_dados.get("ID")
                nome_padrao = operacao_dados.get("nome_operacao") or operacao_dados.get("Operacao") or operacao_dados.get("operacao") or ""
                ativo_padrao = operacao_dados.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
                nome_padrao = ""
                ativo_padrao = True
        else:
            id_padrao = None
            nome_padrao = ""
            ativo_padrao = True
        
        titulo = f"Editando operação: {nome_padrao}" if is_edicao else "Cadastro operação"
        TitlePages(title_page=titulo, btn_nome="Lista de operações", acao_btn=self.mudar_tela, parametro_acao=False).title()
        
        with st.form(key="form_cadastro_operacao", clear_on_submit=not is_edicao):
            col_nome_operacao, col_ativo, espaco = st.columns([6,2,4], vertical_alignment="bottom")
            
            with col_nome_operacao:
                operacao = st.text_input(label="Operação", value=nome_padrao, placeholder="Informe o nome da operação...", key="input_operacao")
            with col_ativo:
                ativo = st.checkbox(label="Ativo", value=ativo_padrao, disabled=not is_edicao, key="checkbox_operacao_ativo")
        
            Divider(color="gray").divider()
            
            btn_cadastrar_alterar_operacao = st.form_submit_button(label="Editar operação" if is_edicao else "Cadastrar operaçao", key="btn_cadastrar_editar_operacao", type="primary")
        if is_edicao:    
            st.button(
                label="Novo", 
                width="stretch", 
                on_click=self.limpar_dados
            )
            
        if btn_cadastrar_alterar_operacao:
            operacao_str = (operacao or "").strip()
        
            try:
                if is_edicao:
                    dados_operacao = OperacaoUpdate(id=id_padrao, nome_operacao=operacao_str, ativo=ativo)
                    self.alterar_dados(operacao_id=id_padrao, operacao_dados=dados_operacao)
                else:
                    dados_operacao = OperacaoCreate(nome_operacao=operacao_str, ativo=ativo)
                    self.salvar_dados(operacao_dados=dados_operacao)
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
        TitlePages(title_page="Lista de operações", btn_nome="Cadastrar operação", acao_btn=self.mudar_tela, parametro_acao=True).title()
        
        operacoes = self.obter_todas_operacoes()
        
        if operacoes:
            dados_operacao = [
                {
                    "ID": op.id,
                    "Operação": op.nome_operacao,
                    "Ativo": "Ativo" if op.ativo else "Inativo"
                }
                for op in operacoes
            ]
            evento_selecao = st.dataframe(data=dados_operacao, on_select="rerun", hide_index=True, selection_mode="single-row")
            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])
            
            if linha_selecionada:
                indice = linha_selecionada[0]
                operacao_selecionada = operacoes[indice]
            
                st.session_state[self.EDITANDO_OPERACAO] = {
                    "indice": indice,
                    "dados": operacao_selecionada
                }
                st.session_state[self.CADASTRO_OPERACAO] = True
                st.rerun()
        else:
            st.write("### Não há operações cadastradas!")
    
    def salvar_dados(self, operacao_dados:OperacaoCreate):
            try:
                with get_db() as db:
                    nova_operacao = OperacaoService.criar_operacao(db=db, operacao_dados=operacao_dados)
                    self.message.definir_mensagem(f"A operação {nova_operacao.nome_operacao} foi cadastrada com sucesso", tipo="success")
                    self.mudar_tela(status=False)
            except (ValueError, ValidationError) as e:
                msg_erro = (
                    e.errors()[0]["msg"]
                    if isinstance(e, ValidationError)
                    else str(e)
                )
                self.message.definir_mensagem(
                    f"Erro ao cadastrar: {msg_erro}", tipo="error"
                )
                
    def alterar_dados(self, operacao_id:int, operacao_dados: OperacaoUpdate):
        try:
            with get_db() as db:
                operacao_atualizada = OperacaoService.alterar_operacao(db=db, operacao_id=operacao_id, dados_operacao=operacao_dados)
                self.message.definir_mensagem(f"A operação {operacao_atualizada.nome_operacao} foi atualizada com sucesso!", tipo="success")
                self.mudar_tela(status=False)
        except (ValueError, ValidationError) as e:
            msg_erro = (
                e.errors()[0]["msg"]
                if isinstance(e, ValidationError)
                else str(e)
            )
            self.message.definir_mensagem(
                f"Erro ao alterar: {msg_erro}", tipo="error"
            )
            
    def obter_todas_operacoes(self):
        try:
            with get_db() as db:
                operacoes = OperacaoService.obter_todas_operacoes(db=db)
                return operacoes
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar operações: {str(e)}", tipo="error"
            )
            return []
    
    def mudar_tela(self, status:bool):
        self.limpar_dados()
        st.session_state[self.CADASTRO_OPERACAO] = status
        st.rerun()
        
    def limpar_dados(self):
        st.session_state[self.EDITANDO_OPERACAO] = None
        st.session_state.pop("operacao_carregado_id", None)
        
            
            
        