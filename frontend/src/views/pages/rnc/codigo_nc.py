import streamlit as st

from components.mensagem import MensagemComponent
from components.title_page import TitlePages
from components.divider import Divider

class CodigoNCPage:
    def __init__(self):
        self.CADASTRO_CODGO_NC = "cadastro_codigo_nc"
        self.EDITANDO_CODIGO_NC = "editando_codigo_nc"
        self.message = MensagemComponent(key_prefix="codigo_nc")
        
        if self.CADASTRO_CODGO_NC not in st.session_state:
            st.session_state[self.CADASTRO_CODGO_NC] = True
        
        if self.EDITANDO_CODIGO_NC not in st.session_state:
            st.session_state[self.EDITANDO_CODIGO_NC] = None
            
    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state.get(self.CADASTRO_CODGO_NC):
            self.cadastro_view()
        else:
            self.lista_view()
            
    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_CODIGO_NC)
        is_edicao = editando is not None
        
        if is_edicao:
            dados_codigo_nc = editando.get("dados")
            
            if hasattr(dados_codigo_nc, "id"):
                id_padrao = dados_codigo_nc.id
                descricao_padrao = getattr(dados_codigo_nc, "descricao", "")
                tipo_padrao = getattr(dados_codigo_nc, "tipo")
                ativo_padrao = getattr(dados_codigo_nc, "ativo", True)
            elif isinstance(dados_codigo_nc, dict):
                id_padrao = dados_codigo_nc.get("id") or dados_codigo_nc("ID")
                descricao_padrao = dados_codigo_nc.get("descricao") or dados_codigo_nc.get("Descricao") or dados_codigo_nc.get("Descrição") or ""
                tipo_padrao = dados_codigo_nc.get("tipo") or ""
                ativo_padrao = dados_codigo_nc.get("ativo", True)
            else:
                id_padrao = None
                is_edicao = False
                descricao_padrao = ""
                tipo_padrao = ""
                ativo_padrao = True
        else:
            id_padrao = None
            descricao_padrao = ""
            tipo_padrao = ""
            ativo_padrao = True
            
        titulo_pagina = f"Editando código: {id_padrao}-Descrição: {descricao_padrao}" if is_edicao else "Cadastro código não conformidade"
        TitlePages(title_page=titulo_pagina, btn_nome="Lista de código NC", acao_btn=self.mudar_tela, parametro_acao=False, tamanho_cols=[8,1,2]).title()
        
        with st.form(key="form_cadastro_codigo_nc", clear_on_submit=not is_edicao):
            col_descricao, col_tipo = st.columns([6, 3], vertical_alignment="bottom")
            
            with col_descricao:
                descricao = st.text_input(label="Descrição", placeholder="Informe a descrição NC", )
            with col_tipo:
                st.selectbox(label="Tipo", options=["Produtiva", "Parada", "Retrabalho"])

            Divider(color="gray").divider()
            
            st.form_submit_button(label="Cadastrar", type="primary", width="content")
        if is_edicao:
            st.button(label="Novo", width="stretch")
    
    def lista_view(self):
        TitlePages(title_page="Lista de códigos não conformidade", btn_nome="Cadastro de código NC", acao_btn=self.mudar_tela, parametro_acao=True, tamanho_cols=[8,1,2]).title()
        
        codigos_nc = []
        
        if codigos_nc:
            tabela_codigo_nc = [
                {
                    "ID": "",
                    "Descrição": "",
                    "Tipo": ""
                }
            ]
            
            st.dataframe(data=tabela_codigo_nc, on_select="rerun", hide_index=True, selection_mode="single-row")
        else:
            st.write(" ### Não há codigos de não conformidade cadastrados!")
    
    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_CODGO_NC] = status
        st.rerun()
