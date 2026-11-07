import streamlit as st

from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from components.divider import Divider

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
                ativo_padrao = None
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
                st.text_input(label="Operação", value=nome_padrao, placeholder="Informe o nome da operação...", key="input_operacao")
            with col_ativo:
                st.checkbox(label="Ativo", value=ativo_padrao, disabled=not is_edicao, key="checkbox_operacao_ativo")
        
            Divider(color="gray").divider()
            
            st.form_submit_button(label="Editar operação" if is_edicao else "Cadastrar operaçao", key="btn_cadastrar_editar_operacao", type="primary")
        if is_edicao:    
            st.button(
                label="Novo", 
                width="stretch", 
                on_click=self.limpar_dados
            )
        
    def lista_view(self):
        TitlePages(title_page="Lista de operações", btn_nome="Cadastrar operação", acao_btn=self.mudar_tela, parametro_acao=True).title()
        
        operacoes = self.obter_todas_operacoes()
        
        if operacoes:
            dados_operacao = [
                {
                    "ID": "",
                    "Operação": "",
                    "Ativo": ""
                }
            ]
            evento_selecao = st.dataframe(data=dados_operacao, on_select="rerun", hide_index=True, selection_mode="single-row")
            linha_selecionada = evento_selecao.get("selection", []).get("rows", {})
            
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
            
    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_OPERACAO] = status
        st.rerun()
        
    def obter_todas_operacoes(self):
        pass
            
            
        