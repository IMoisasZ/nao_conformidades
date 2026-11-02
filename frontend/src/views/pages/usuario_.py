"""Módulo da Página de Usuários (Frontend Streamlit)."""

import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.models.usuario_model import TipoUsuario
from backend.src.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioUpdate,
)
from backend.src.services.usuario_service import UsuarioService
from components.button import ButtonComponent
from components.checkbox import CheckboxComponent
from components.divider import Divider
from components.mensagem import MensagemComponent
from components.select import SelectComponent
from components.title_page import TitlePages
from views.pages.usuario_setores import UsuarioSetoresPage


class UsuarioPage:
    def __init__(self):
        self.USUARIO_VIEW_ATUAL = "usuario_view_atual"
        self.EDITANDO_USUARIO = "editando_usuario"
        self.SENHA_DESATIVADA = "senha_desativada"
        self.ALTERACAO_SENHA = "alteracao_senha"
        self.MODAL_SENHA_ABERTA = "modal_senha_aberta"
        self.message = MensagemComponent(key_prefix="usuario")

        if self.USUARIO_VIEW_ATUAL not in st.session_state:
            st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"

        if self.EDITANDO_USUARIO not in st.session_state:
            st.session_state[self.EDITANDO_USUARIO] = None

        if self.SENHA_DESATIVADA not in st.session_state:
            st.session_state[self.SENHA_DESATIVADA] = False

        if self.ALTERACAO_SENHA not in st.session_state:
            st.session_state[self.ALTERACAO_SENHA] = False

        if self.MODAL_SENHA_ABERTA not in st.session_state:
            st.session_state[self.MODAL_SENHA_ABERTA] = False

        if "temp_senha" not in st.session_state:
            st.session_state["temp_senha"] = None

        if "temp_conf_senha" not in st.session_state:
            st.session_state["temp_conf_senha"] = None

    def renderizar(self):
        self.message.exibir_mensagem()
        view = st.session_state.get(self.USUARIO_VIEW_ATUAL)

        match view:
            case "cadastro":
                self.cadastro_view()
            case "lista":
                self.lista_view()
            case "setores":
                dados_usuario = st.session_state.get(self.EDITANDO_USUARIO)
                usuario_id = dados_usuario["dados"].id
                usuario_nome = dados_usuario["dados"].nome
                UsuarioSetoresPage(
                    usuario_id=usuario_id, usuario_nome=usuario_nome
                ).renderizar()

    def cadastro_view(self):
        TitlePages(
            title_page="Usuários",
            btn_nome="Lista de usuários",
            acao_btn=self.mudar_tela,
            parametro_acao=False,
        ).title()

        editando = st.session_state.get(self.EDITANDO_USUARIO)
        is_edicao = editando is not None

        # 1. CARGA E SINCRONIZAÇÃO DE DADOS EM EDIÇÃO
        if is_edicao:
            usuario_dados = editando["dados"]
            id_padrao = usuario_dados.id

            if st.session_state.get("usuario_carregado_id") != id_padrao:
                st.session_state["input_codigo_usuario"] = (
                    str(usuario_dados.codigo)
                    if usuario_dados.codigo is not None
                    else ""
                )
                st.session_state["input_nome_usuario"] = usuario_dados.nome or ""
                st.session_state["input_email_usuario"] = usuario_dados.email or ""

                val_tipo = usuario_dados.tipo_usuario
                st.session_state["select_tipo_usuario"] = (
                    val_tipo.value if hasattr(val_tipo, "value") else str(val_tipo)
                )
                st.session_state["usuario_carregado_id"] = id_padrao
        else:
            id_padrao = None

        # 2. INSTANCIAÇÃO DIRETA DO ST.TEXT_INPUT NATIVO
        codigo_col, nome_col, email_col = st.columns([2, 4, 4])
        with codigo_col:
            codigo = st.text_input(
                label="Código",
                key="input_codigo_usuario",
                placeholder="Informe o código do usuário...",
            )
        with nome_col:
            nome = st.text_input(
                label="Nome",
                key="input_nome_usuario",
                placeholder="Informe o nome do usuário...",
            )
        with email_col:
            email = st.text_input(
                label="Email",
                key="input_email_usuario",
                placeholder="Informe o email do usuário...",
            )

        tipo_usuario_col, senha_col, confirmacao_col = st.columns([2, 4, 4])
        with tipo_usuario_col:
            options_tipo = [tipo.value for tipo in TipoUsuario]
            tipo_usuario_str = SelectComponent(
                label="Tipo usuário",
                key="select_tipo_usuario",
                options=options_tipo,
            ).select()
        with senha_col:
            senha = st.text_input(
                label="Senha",
                type="password",
                placeholder="Informe a senha de 5 números...",
                key="input_senha_usuario",
                disabled=is_edicao,
            )
        with confirmacao_col:
            confirmacao_senha = st.text_input(
                label="Confirmação da senha",
                type="password",
                placeholder="Confirme a senha informada...",
                key="input_confirmacao_senha",
                disabled=is_edicao,
            )

        ativo = CheckboxComponent(
            label="Ativo",
            value=True,
            disabled=False if is_edicao else True,
        ).checkbox()

        Divider(color="gray").divider()

        # 3. BOTÕES DE AÇÃO
        if is_edicao:
            (
                btn_cadastro_col,
                btn_novo_col,
                btn_alterar_senha,
                btn_setores_col,
            ) = st.columns(4, vertical_alignment="bottom")
            with btn_cadastro_col:
                btn_cadastro_alteracao = ButtonComponent(
                    label="Editar usuário",
                    key="btn_cadastrar_alterar_usuario",
                ).btn()
            with btn_novo_col:
                btn_novo = ButtonComponent(
                    label="Novo",
                    onclick=self.limpar_dados,
                    key="btn_novo_usuario",
                ).btn()
            with btn_alterar_senha:
                if ButtonComponent(
                    label="Alterar senha", key="btn_alterar_senha"
                ).btn():
                    st.session_state[self.MODAL_SENHA_ABERTA] = True
                    st.session_state["modal_usuario_id"] = id_padrao
                    st.session_state["modal_usuario_nome"] = nome
                    st.rerun()
            with btn_setores_col:
                btn_setores = ButtonComponent(
                    label="Setores sob responsabilidade",
                    onclick=self.mudar_tela_setores,
                    args=["setores"],
                    key="btn_setores",
                ).btn()
        else:
            btn_cadastro_col, btn_novo_col = st.columns(
                2, vertical_alignment="bottom"
            )
            with btn_cadastro_col:
                btn_cadastro_alteracao = ButtonComponent(
                    label="Cadastrar usuário",
                    key="btn_cadastrar_alterar_usuario",
                ).btn()
            with btn_novo_col:
                btn_novo = ButtonComponent(
                    label="Novo",
                    onclick=self.limpar_dados,
                    key="btn_novo_usuario",
                ).btn()

        # 4. PROCESSAMENTO DO SUBMIT
        if btn_cadastro_alteracao:
            # Leitura direta do session_state via key nativa
            codigo_val = st.session_state.get("input_codigo_usuario", "")
            nome_str = str(st.session_state.get("input_nome_usuario", "")).strip()
            email_str = str(st.session_state.get("input_email_usuario", "")).strip()
            senha_str = str(st.session_state.get("input_senha_usuario", "")).strip()
            confirmacao_str = str(
                st.session_state.get("input_confirmacao_senha", "")
            ).strip()

            try:
                codigo_int = (
                    int(codigo_val)
                    if codigo_val and str(codigo_val).strip().isdigit()
                    else None
                )
                tipo_enum = TipoUsuario(tipo_usuario_str)

                if is_edicao:
                    dados_usuario = UsuarioUpdate(
                        id=id_padrao,
                        nome=nome_str,
                        email=email_str,
                        tipo_usuario=tipo_enum,
                        ativo=ativo,
                    )
                    self.alterar_dados(usuario_id=id_padrao, dados=dados_usuario)
                else:
                    if not senha_str:
                        raise ValueError("A senha deve ser informada!")
                    if len(senha_str) != 5:
                        raise ValueError(
                            "A senha deve conter exatamente 5 caracteres!"
                        )
                    if senha_str != confirmacao_str:
                        raise ValueError("As senhas não conferem!")

                    dados_usuario = UsuarioCreate(
                        codigo=codigo_int,
                        nome=nome_str,
                        email=email_str,
                        tipo_usuario=tipo_enum,
                        senha=senha_str,
                        ativo=ativo,
                    )
                    self.salvar_dados(dados=dados_usuario)

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

        # 5. MODAL DE SENHA
        if st.session_state.get(self.MODAL_SENHA_ABERTA, False):
            self.renderizar_alteracao_senha(
                usuario_id=st.session_state.get("modal_usuario_id"),
                nome_usuario=st.session_state.get("modal_usuario_nome"),
            )

    def alterar_senha_view(self, usuario_id: int, nome_usuario: str):
        st.write(f"Usuário: **{nome_usuario}**")

        if "erro_modal_senha" in st.session_state:
            st.error(st.session_state["erro_modal_senha"])

        with st.form(key="form_alteracao_senha_modal", clear_on_submit=False):
            nova_senha = st.text_input(
                label="Nova senha",
                type="password",
                key="modal_form_nova_senha",
            )

            conf_nova_senha = st.text_input(
                label="Confirmar nova senha",
                type="password",
                key="modal_form_conf_nova_senha",
            )

            btn_alterar_col, btn_cancelar_col = st.columns(2)
            with btn_alterar_col:
                btn_alterar = st.form_submit_button(
                    "Avançar", type="primary", use_container_width=True
                )
            with btn_cancelar_col:
                btn_cancelar = st.form_submit_button(
                    "Cancelar", use_container_width=True
                )

            if btn_alterar:
                s1 = str(st.session_state.get("modal_form_nova_senha", "")).strip()
                s2 = str(
                    st.session_state.get("modal_form_conf_nova_senha", "")
                ).strip()

                dados_alterar = {
                    "id": usuario_id,
                    "senha": s1,
                    "conf_senha": s2,
                }

                valido, msg_erro = self.validacao_alteracao_senha(
                    dados=dados_alterar
                )

                if valido:
                    st.session_state["temp_senha"] = s1
                    st.session_state["temp_conf_senha"] = s2
                    st.session_state[self.ALTERACAO_SENHA] = True
                    st.session_state.pop("erro_modal_senha", None)
                    st.rerun()
                else:
                    st.session_state["erro_modal_senha"] = msg_erro
                    st.rerun()

        if btn_cancelar:
            self.fechar_modal_senha()
            st.rerun()

    def lista_view(self):
        TitlePages(
            title_page="Usuários",
            btn_nome="Cadastrar usuário",
            acao_btn=self.mudar_tela,
            parametro_acao="cadastro",
        ).title()

        usuarios = self.obter_todos_usuarios()

        if usuarios:
            dados_usuarios = [
                {
                    "ID": user.id,
                    "Codigo": user.codigo,
                    "Nome": user.nome,
                    "Email": user.email,
                    "Tipo usuario": user.tipo_usuario,
                    "Ativo": "Ativo" if user.ativo else "Inativo",
                }
                for user in usuarios
            ]
            evento_selecao = st.dataframe(
                data=dados_usuarios,
                width="stretch",
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
            )

            linha_selecionada = evento_selecao.get("selection", {}).get(
                "rows", []
            )

            if linha_selecionada:
                indice = linha_selecionada[0]
                usuario_selecionado = usuarios[indice]

                st.session_state[self.EDITANDO_USUARIO] = {
                    "idice": indice,
                    "dados": usuario_selecionado,
                }

                st.session_state[self.USUARIO_VIEW_ATUAL] = "cadastro"
                st.session_state[self.SENHA_DESATIVADA] = True
                st.rerun()
        else:
            st.write(" ### Não há usuários cadastrados!")

    def salvar_dados(self, dados: UsuarioCreate):
        try:
            with get_db() as db:
                novo_usuario = UsuarioService.criar_usuario(
                    db=db, usuario_dados=dados
                )
                self.message.definir_mensagem(
                    f"O usuário {novo_usuario.nome} foi cadastrado com sucesso!",
                    tipo="success",
                )

                st.session_state[self.EDITANDO_USUARIO] = None
                st.session_state["usuario_carregado_id"] = None
                st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"
                st.rerun()
        except ValidationError as e:
            msg_erro = e.errors()[0]["msg"]
            self.message.definir_mensagem(
                f"Erro de validação: {msg_erro}", tipo="error"
            )
        except ValueError as e:
            self.message.definir_mensagem(str(e), tipo="error")
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro no banco de dados: {str(e)}", tipo="error"
            )

    def alterar_dados(self, usuario_id: int, dados: UsuarioUpdate):
        try:
            with get_db() as db:
                usuario_atualizado = UsuarioService.alterar_usuario(
                    db=db, usuario_id=usuario_id, usuario_dados=dados
                )
                self.message.definir_mensagem(
                    f"O usuário {usuario_atualizado.nome} foi alterado com sucesso",
                    tipo="success",
                )

                st.session_state[self.EDITANDO_USUARIO] = None
                st.session_state["usuario_carregado_id"] = None
                st.session_state[self.USUARIO_VIEW_ATUAL] = "lista"
                st.rerun()
        except ValidationError as e:
            msg_erro = e.errors()[0]["msg"]
            self.message.definir_mensagem(
                f"Erro de validação: {msg_erro}", tipo="error"
            )
        except ValueError as e:
            self.message.definir_mensagem(str(e), tipo="error")
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro no banco de dados: {str(e)}", tipo="error"
            )

    def obter_todos_usuarios(self):
        try:
            with get_db() as db:
                return UsuarioService.obter_todos_usuarios(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar usuários: {str(e)}", tipo="error"
            )
            return []

    def mudar_tela(self, view: str):
        st.session_state[self.USUARIO_VIEW_ATUAL] = view
        self.limpar_dados()

    def mudar_tela_setores(self, view: str):
        st.session_state[self.USUARIO_VIEW_ATUAL] = view
        st.rerun()

    def limpar_dados(self):
        st.session_state[self.EDITANDO_USUARIO] = None
        st.session_state[self.SENHA_DESATIVADA] = False
        st.session_state[self.ALTERACAO_SENHA] = False
        st.session_state[self.MODAL_SENHA_ABERTA] = False
        st.session_state["usuario_carregado_id"] = None

        st.session_state["input_codigo_usuario"] = ""
        st.session_state["input_nome_usuario"] = ""
        st.session_state["input_email_usuario"] = ""
        st.session_state["select_tipo_usuario"] = (
            TipoUsuario.USUARIO.value
            if hasattr(TipoUsuario.USUARIO, "value")
            else str(TipoUsuario.USUARIO)
        )
        st.session_state["input_senha_usuario"] = ""
        st.session_state["input_confirmacao_senha"] = ""

        st.session_state.pop("modal_usuario_id", None)
        st.session_state.pop("modal_usuario_nome", None)
        st.session_state.pop("temp_senha", None)
        st.session_state.pop("temp_conf_senha", None)
        st.session_state.pop("erro_modal_senha", None)

        st.rerun()

    def fechar_modal_senha(self):
        st.session_state[self.MODAL_SENHA_ABERTA] = False
        st.session_state[self.ALTERACAO_SENHA] = False
        st.session_state.pop("temp_senha", None)
        st.session_state.pop("temp_conf_senha", None)
        st.session_state.pop("erro_modal_senha", None)
        st.session_state.pop("modal_form_nova_senha", None)
        st.session_state.pop("modal_form_conf_nova_senha", None)
        self.limpar_dados()

    @st.dialog("Alteração de senha")
    def renderizar_alteracao_senha(self, usuario_id: int, nome_usuario: str):
        if st.session_state.get(self.ALTERACAO_SENHA, False):
            self.confirmar_alteracao_senha_view(
                nome_usuario=nome_usuario, usuario_id=usuario_id
            )
        else:
            self.alterar_senha_view(
                usuario_id=usuario_id, nome_usuario=nome_usuario
            )

    def confirmar_alteracao_senha_view(
        self, nome_usuario: str, usuario_id: int
    ):
        st.write(
            f"Confirma a alteração da senha do usuário **{nome_usuario}**?"
        )
        confirma_col, cancela_col = st.columns(2)

        with confirma_col:
            confirma_btn = ButtonComponent(
                label="Confirmar", key="btn_confirmar_final_modal"
            ).btn()
        with cancela_col:
            cancela_btn = ButtonComponent(
                label="Cancelar", key="btn_cancelar_final_modal"
            ).btn()

        if confirma_btn:
            nova_senha_para_gravar = st.session_state.get("temp_senha")

            with get_db() as db:
                try:
                    UsuarioService.alterar_senha(
                        db=db,
                        usuario_id=usuario_id,
                        nova_senha=nova_senha_para_gravar,
                    )
                    self.fechar_modal_senha()
                    self.message.definir_mensagem(
                        "Senha alterada com sucesso!", tipo="success"
                    )
                    st.rerun()
                except ValidationError as e:
                    msg_erro = e.errors()[0]["msg"]
                    self.message.definir_mensagem(
                        f"Erro de validação: {msg_erro}", tipo="error"
                    )
                except ValueError as e:
                    self.message.definir_mensagem(str(e), tipo="error")
                except Exception as e:
                    self.message.definir_mensagem(
                        f"Erro no banco de dados: {str(e)}", tipo="error"
                    )

        if cancela_btn:
            self.fechar_modal_senha()
            st.rerun()

    def validacao_alteracao_senha(self, dados: dict) -> tuple[bool, str]:
        id_usuario = dados.get("id")
        senha = (dados.get("senha") or "").strip()
        conf_senha = (dados.get("conf_senha") or "").strip()

        if not id_usuario:
            return (False, "ID do usuário não informado!")
        elif not senha:
            return (False, "A senha deve ser informada")
        elif len(senha) != 5:
            return (False, "A senha deve conter 5 caracteres!")
        elif not conf_senha:
            return (False, "A confirmação da senha deve ser informada")
        elif senha != conf_senha:
            return (False, "As senhas não conferem!")
        else:
            return (True, "")