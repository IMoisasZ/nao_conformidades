import streamlit as st
from pydantic import ValidationError

from components.title_page import TitlePages
from components.input import InputComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider
from components.mensagem import MensagemComponent

from backend.src.connection.db_connection import get_db
from backend.src.schemas.empresa_schema import EmpresaCreate, EmpresaUpdate
from backend.src.services.empresa_service import EmpresaService

class EmpresaPage:
    def __init__(self):
        self.CADASTRO_EMPRESA = "cadastro_empresa"
        self.EDITANDO_EMPRESA = "editando_empresa"
        self.message = MensagemComponent(key_prefix="empresa")

        if self.CADASTRO_EMPRESA not in st.session_state:
            st.session_state[self.CADASTRO_EMPRESA] = False
            
        if self.EDITANDO_EMPRESA not in st.session_state:
            st.session_state[self.EDITANDO_EMPRESA] = None
    
    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_EMPRESA]:
            self.cadastro_view()
        else:
            self.lista_view()
    
    def cadastro_view(self):
        TitlePages(title_page="Cadastro empresa", btn_nome="Lista de empresas", acao_btn=self.mudar_tela, parametro_acao=False).title()
        
        editando = st.session_state.get(self.EDITANDO_EMPRESA)
        is_edicao = editando is not None
        
        if is_edicao:
            id_padrao = (editando["dados"].id)
            if "input_nome_empresa" not in st.session_state:
                st.session_state["input_nome_empresa"] = (editando["dados"].nome_empresa)
            
            if "input_cnpj" not in st.session_state:    
                st.session_state["input_cnpj"] = editando["dados"].cnpj
            
            if "checkbox_ativo" not in st.session_state:
                st.session_state["checkbox_ativo"] = editando["dados"].ativo
        else:
            id_padrao = None
            
        empresa_col, cnpj_col, ativo_col = st.columns([4,4,2], vertical_alignment="bottom")
        with empresa_col:
            empresa = InputComponent(label="Nome empresa", key="input_nome_empresa", placeholder="Informe o nome da empresa...").input()
        with cnpj_col:
            cnpj = InputComponent(label="CNPJ", placeholder="Informe o numero do CNPJ da empresa: Ex: 12.123.456/0001-89", key="input_cnpj").input()
        with ativo_col:
            ativo = CheckboxComponent(label="Ativo", disabled=False if st.session_state[self.EDITANDO_EMPRESA] else True, key="checkbox_ativo", value=True).checkbox()
            
        Divider(color="gray").divider()
        btn_cadastro, btn_novo = st.columns(2)
        with btn_cadastro:
            btn_cadastro_alteracao = ButtonComponent(label="Editar empresa" if st.session_state[self.EDITANDO_EMPRESA] else "Cadastrar empresa", key="btn_cadastrar_alterar_empresa").btn()
        with btn_novo:
            nova_empresa = ButtonComponent(label="Novo", onclick=self.limpar_dados).btn()
            
        
        if btn_cadastro_alteracao:
            try:
                if is_edicao:
                    dados_empresa = EmpresaUpdate(id=id_padrao, nome_empresa=empresa, cnpj=cnpj, ativo=ativo)
                    self.alterar_dados(empresa_id=id_padrao, dados_empresa=dados_empresa)
                else:
                    dados_empresa = EmpresaCreate(nome_empresa=empresa, cnpj=cnpj, ativo=ativo)
                    self.salvar_dados(dados=dados_empresa)
            except ValidationError as e:
                msg_erro = e.errors()[0]["msg"]
                self.message.definir_mensagem(f"Erro de validação: {msg_erro}", tipo="error")
                st.rerun()
                
    def lista_view(self):
        TitlePages(title_page="Lista de empresas", btn_nome="Cadastro empresa", acao_btn=self.mudar_tela, parametro_acao=True).title()
        
        empresas = self.obter_todas_empresas()

        if empresas:        
            dados_empresas_db = [
                {
                    "ID": emp.id,
                    "Empresa":emp.nome_empresa,
                    "CNPJ": emp.cnpj,
                    "Ativo": "Ativo" if emp.ativo else "Intativo"
                }
                for emp in empresas
            ]
            evento_selecao = st.dataframe(data=dados_empresas_db, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")
            
            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])
            
            if linha_selecionada:
                indice = linha_selecionada[0]
                empresa_selecionada = empresas[indice]
                
                st.session_state[self.EDITANDO_EMPRESA] = {
                    "indice": indice,
                    "dados": empresa_selecionada
                }
                
                st.session_state[self.CADASTRO_EMPRESA] = True
                st.rerun()
        else:
            self.message.definir_mensagem("Nenhuma empresa cadastrada.", tipo="info")
        
    def salvar_dados(self, dados:EmpresaCreate):
        try:
            with get_db() as db:
                nova_empresa = EmpresaService.criar_empresa(db=db, empresa_dados=dados)
                self.message.definir_mensagem(f"A empresa {nova_empresa.nome_empresa} foi criada com sucesso!", tipo="success")
                self.limpar_dados()
                self.mudar_tela(status=False)
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()
    
    def alterar_dados(self, empresa_id:int, dados_empresa: EmpresaUpdate):
        try:
            with get_db() as db:
                empresa_atualizada = EmpresaService.alterar_empresa(db=db, empresa_id=empresa_id, empresa_dados=dados_empresa)
                self.message.definir_mensagem(f"A empresa {empresa_atualizada.nome_empresa} foi atualizada com sucesso!", tipo="success")
                self.limpar_dados()
                self.mudar_tela(status=False)
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()
    
    def obter_todas_empresas(self):
        try:
            with get_db() as db:
                empresas = EmpresaService.obter_todas_empresas(db=db)
                return empresas
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar empresas: {str(e)}", tipo="error")
            return []      
        
    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_EMPRESA] = status
        st.rerun()
        
    def limpar_dados(self):
        st.session_state[self.EDITANDO_EMPRESA] = None
        st.session_state.pop("input_nome_empresa", None)
        st.session_state.pop("input_cnpj", None)
        st.session_state.pop("checkbox_ativo", None)