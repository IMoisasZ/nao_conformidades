import streamlit as st
from pydantic import ValidationError

from components.title_page import TitlePages
from components.input import InputComponent
from components.select import SelectComponent
from components.checkbox import CheckboxComponent
from components.button import ButtonComponent
from components.divider import Divider
from components.mensagem import MensagemComponent

from backend.src.connection.db_connection import get_db
from backend.src.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha, UsuarioResponse
from backend.src.services.usuario_service import UsuarioService
class UsuarioPage:
    def __init__(self):
        self.CADASTRO_USUARIO = "cadastro_usuario"
        self.EDITANDO_USUARIO = "editando_usuario"
        self.message = MensagemComponent(key_prefix="empresa")
        
        if self.CADASTRO_USUARIO not in st.session_state:
            st.session_state[self.CADASTRO_USUARIO] = False
            
        if self.EDITANDO_USUARIO not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO] = None
    
    def renderizar(self):
        self.message.exibir_mensagem()
        if st.session_state[self.CADASTRO_USUARIO]:
            self.cadastro_view()
        else:
            self.lista_view()
    
    def cadastro_view(self):
        TitlePages(title_page="Usuários", btn_nome="Lista de usuários", acao_btn=self.mudar_tela, parametro_acao=False).title()

        editando = st.session_state.get(self.EDITANDO_USUARIO)
        is_edicao = editando is not None

        if is_edicao:
            id_padrao = editando["dados"].id
            if "input_codigo_usuario" not in st.session_state:
                st.session_state["input_codigo_usuario"] = editando["dados"].codigo

            if "input_nome_usuario" not in st.session_state:
                st.session_state["input_nome_usuario"] = editando["dados"].nome

            if "input_email_usuario" not in st.session_state:
                st.session_state["input_email_usuario"] = editando["dados"].email

            if "select_tipo_usuario" not in st.session_state:
                st.session_state["select_tipo_usuario"] = editando["dados"].tipo_usuario
        else:
            id_padrao = None

        codigo_col, nome_col, email_col = st.columns([2, 4, 4])
        with codigo_col:
            codigo = InputComponent(label="Codigo", key="input_codigo_usuario", placeholder="Informe o código do usuário...").input()
        with nome_col:
            nome = InputComponent(label="Nome", key="input_nome_usuario", placeholder="Informe o nome do usuario...").input()
        with email_col:
            email = InputComponent(label="Email", key="input_email_usuario", placeholder="Informe o email do usuario...", type="email").input()
            
        tipo_usuario_col, senha_col, confirmacao_col = st.columns([2, 4, 4])
        with tipo_usuario_col:
            tipo_usuario = SelectComponent(label="Tipo usuario", key="select_tipo_usuario", options=["Usuario", "Supervisor", "Administrador", "Master"]).select()
        with senha_col:
            senha = InputComponent(label="Senha", type="password", placeholder="Informe a senha de 5 numeros...").input()
        with confirmacao_col:
            confirmacao_senha = InputComponent(label="Confirmação da senha", type="password", placeholder="Confirme a senha informada...").input()
        
        ativo = CheckboxComponent(label="Ativo", value=True, disabled=False if st.session_state[self.EDITANDO_USUARIO] else True).checkbox()
        
        Divider(color="gray").divider()
        
        btn_cadastro_col, btn_novo_col = st.columns(2, vertical_alignment="bottom")
        with btn_cadastro_col:
            btn_cadastro_alteracao = ButtonComponent(label="Editar usuario" if st.session_state[self.EDITANDO_USUARIO] else "Cadastrar usuario", key="btn_cadastrar_alterar_usuario").btn()
        with btn_novo_col:
            btn_novo = ButtonComponent(label="Novo").btn()  

        if btn_cadastro_alteracao:
            print(btn_cadastro_alteracao)
            try:
                if is_edicao:
                    dados_usuario = UsuarioUpdate(id=id_padrao, nome=nome, email=email, tipo_usuario=tipo_usuario, ativo=ativo)
                    self.alterar_dados(usuario_id=id_padrao, dados=dados_usuario)
                else:
                    dados_usuario = UsuarioCreate(codigo=codigo, nome=nome, email=email, tipo_usuario=tipo_usuario, senha=senha)
                    self.salvar_dados(dados=dados_usuario)
            except ValidationError as e:
                msg_erro = e.errors()[0]["msg"]
                self.message.definir_mensagem(f"Erro de validação: {msg_erro}", tipo="error")
                st.rerun()
    
    def lista_view(self):
        TitlePages(title_page="Usuários", btn_nome="Cadastrar usuário", acao_btn=self.mudar_tela, parametro_acao=True).title()

        usuarios = self.obter_todos_usuarios()

        if usuarios:
            dados_usuarios = [
                {
                    "ID": "",
                    "Codigo": "",
                    "Nome": "",
                    "Tipo usuario": "",
                    "Ativo": ""
                }
                for user in usuarios
            ]
            evento_selecao = st.dataframe(data=dados_usuarios, width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row")

            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])

            if linha_selecionada:
                indice = linha_selecionada[0]
                usuario_selecionado = usuarios[indice]

                st.session_state[self.EDITANDO_USUARIO] = {
                    "idice": indice,
                    "dados": usuario_selecionado
                }

                st.session_state[self.CADASTRO_USUARIO] = True
                st.rerun()

    def salvar_dados(self, dados:UsuarioCreate):
        try:
            with get_db() as db:
                novo_usuario = UsuarioService.criar_usuario(db=db, usuario_dados=dados)
                self.message.definir_mensagem(f"O usuário {novo_usuario.nome} foi cadastrado com sucesso!", tipo="success")
                self.limpar_dados()
                self.mudar_tela(status=False)
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()

    def alterar_dados(self, usuario_id:int, dados:UsuarioUpdate):
        try:
            with get_db() as db:
                usuario_atualizado = UsuarioService.alterar_usuario(db=db, usuario_id=usuario_id, usuario_dados=dados)
                self.message.definir_mensagem(f"O usuário {usuario_atualizado.nome} foi alterado com sucesso", tipo="success")
                self.limpar_dados()
                self.mudar_tela(status=False)
        except (ValueError, ValidationError) as e:
            msg_erro = e.errors()[0]["msg"] if isinstance(e, ValidationError) else str(e)
            self.message.definir_mensagem(f"Erro ao cadastrar: {msg_erro}", tipo="error")
            st.rerun()

    def obter_todos_usuarios(self):
        try:
            with get_db() as db:
                usuarios = UsuarioService.obter_todos_usuarios(db=db)
                return usuarios
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar empresas: {str(e)}", tipo="error")
            return []             

    def mudar_tela(self, status:bool):
        st.session_state[self.CADASTRO_USUARIO] = status
        st.rerun()