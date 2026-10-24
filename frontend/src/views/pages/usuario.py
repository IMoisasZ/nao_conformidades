import streamlit as st

from components.title_page import TitlePages
from components.input import InputComponent
from components.select import SelectComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider

class UsuarioPage:
    def __init__(self):
        self.CADASTRO_USUARIO = "cadastro_usuario"
        self.EDITANDO_USUARIO = "editando_usuario"
        
        if self.CADASTRO_USUARIO not in st.session_state:
            st.session_state[self.CADASTRO_USUARIO] = False
            
        if self.EDITANDO_USUARIO not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO] = None
    
    def renderizar(self):
        if st.session_state[self.CADASTRO_USUARIO]:
            self.cadastro_view()
        else:
            self.lista_view()
    
    def cadastro_view(self):
        TitlePages(title_page="Usuários", btn_nome="Lista de usuários", acao_btn=self.mudar_tela, parametro_acao=False).title()
        
        codigo_col, nome_col, email_col = st.columns([2, 4, 4])
        with codigo_col:
            codigo = InputComponent(label="Codigo", placeholder="Informe o código do usuário...").input()
        with nome_col:
            nome = InputComponent(label="Nome", placeholder="Informe o nome do usuario...").input()
        with email_col:
            email = InputComponent(label="Email", placeholder="Informe o email do usuario...", type="email").input()
            
        tipo_usuario_col, senha_col, confirmacao_col = st.columns([2, 4, 4])
        with tipo_usuario_col:
            tipo_usuario = SelectComponent(label="Tipo usuario", options=["Usuario", "Supervisor", "Administrador", "Master"]).select()
        with senha_col:
            senha = InputComponent(label="Senha", type="password", placeholder="Informe a senha de 5 numeros...").input()
        with confirmacao_col:
            confirmacao_senha = InputComponent(label="Confirmação da senha", type="password", placeholder="Confirme a senha informada...").input()
        
        ativo = CheckboxComponent(label="Ativo", value=True, disabled=False if st.session_state[self.EDITANDO_USUARIO] else True).checkbox()
        
        Divider(color="gray").divider()
        
        btn_cadastro_col, btn_novo_col = st.columns(2, vertical_alignment="bottom")
        with btn_cadastro_col:
            btn_cadastro_alteracao = ButtonComponent(label="Editar usuario" if st.session_state[self.EDITANDO_USUARIO] else "Cadastrar usuario").btn()
        with btn_novo_col:
            btn_novo = ButtonComponent(label="Novo").btn()
        
        
    
    def lista_view(self):
        TitlePages(title_page="Usuários", btn_nome="Cadastrar usuário", acao_btn=self.mudar_tela, parametro_acao=True).title()
        
        dados_usuarios = [
            {
                "ID": "",
                "Codigo": "",
                "Nome": "",
                "Tipo usuario": "",
                "Ativo": ""
            }
        ]
        
        st.dataframe(data=dados_usuarios)
        
    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_USUARIO] = status
        st.rerun()