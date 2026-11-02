import streamlit as st
from pydantic import ValidationError

from backend.src.connection.db_connection import get_db
from backend.src.schemas.empresa_schema import EmpresaCreate, EmpresaUpdate
from backend.src.services.empresa_service import EmpresaService
from components.button import ButtonComponent
from components.checkbox import CheckboxComponent
from components.divider import Divider
from components.input import InputComponent
from components.mensagem import MensagemComponent
from components.title_page import TitlePages


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
        

        editando = st.session_state.get(self.EDITANDO_EMPRESA)
        is_edicao = editando is not None

        if is_edicao:
            id_padrao = editando["dados"].id
            nome_padrao = editando["dados"].nome_empresa or ""
            cnpj_padrao = editando["dados"].cnpj or ""
            ativo_padrao = editando["dados"].ativo
        else:
            id_padrao = None
            nome_padrao = ""
            cnpj_padrao = ""
            ativo_padrao = True
            
        titulo_pagina = f"Editar empresa: {nome_padrao}" if is_edicao else "Cadastrar empresa"
        TitlePages(
            title_page=titulo_pagina,
            btn_nome="Lista de empresas",
            acao_btn=self.mudar_tela,
            parametro_acao=False,
            tamanho_cols=[9,1,2]
        ).title()

        # Formulário que congela e captura os valores dos campos
        with st.form(key="form_cadastro_empresa", clear_on_submit=not is_edicao):
            empresa_col, cnpj_col, ativo_col = st.columns(
                [4, 4, 2], vertical_alignment="bottom"
            )
            with empresa_col:
                empresa = st.text_input(
                    label="Nome empresa",
                    value=nome_padrao,
                    placeholder="Informe o nome da empresa...",
                )
            with cnpj_col:
                cnpj = st.text_input(
                    label="CNPJ",
                    value=cnpj_padrao,
                    placeholder="Informe o número do CNPJ: Ex: 12.123.456/0001-89",
                )
            with ativo_col:
                ativo = st.checkbox(
                    label="Ativo",
                    value=ativo_padrao,
                    disabled=not is_edicao,
                )

            Divider(color="gray").divider()

            btn_label = (
                "Editar empresa" if is_edicao else "Cadastrar empresa"
            )
            btn_cadastro_alteracao = st.form_submit_button(
                label=btn_label, type="primary"
            )

        if is_edicao:
            st.button(
                label="Novo",
                width="stretch",
                on_click=self.limpar_dados,
            )

        if btn_cadastro_alteracao:
            empresa_str = (empresa or "").strip()
            cnpj_str = (cnpj or "").strip()

            try:
                if is_edicao:
                    dados_empresa = EmpresaUpdate(
                        id=id_padrao,
                        nome_empresa=empresa_str,
                        cnpj=cnpj_str,
                        ativo=ativo,
                    )
                    self.alterar_dados(
                        empresa_id=id_padrao, dados_empresa=dados_empresa
                    )
                else:
                    dados_empresa = EmpresaCreate(
                        nome_empresa=empresa_str,
                        cnpj=cnpj_str,
                        ativo=ativo,
                    )
                    self.salvar_dados(dados=dados_empresa)
            except ValidationError as e:
                msg_erro = e.errors()[0]["msg"]
                self.message.definir_mensagem(
                    f"Erro de validação: {msg_erro}", tipo="error"
                )

    def lista_view(self):
        TitlePages(
            title_page="Lista de empresas",
            btn_nome="Cadastro empresa",
            acao_btn=self.mudar_tela,
            parametro_acao=True,
        ).title()

        empresas = self.obter_todas_empresas()

        if empresas:
            dados_empresas_db = [
                {
                    "ID": emp.id,
                    "Empresa": emp.nome_empresa,
                    "CNPJ": emp.cnpj,
                    "Ativo": "Ativo" if emp.ativo else "Inativo",
                }
                for emp in empresas
            ]
            evento_selecao = st.dataframe(
                data=dados_empresas_db,
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
                empresa_selecionada = empresas[indice]

                st.session_state[self.EDITANDO_EMPRESA] = {
                    "indice": indice,
                    "dados": empresa_selecionada,
                }

                st.session_state[self.CADASTRO_EMPRESA] = True
                st.rerun()
        else:
            st.write(" ### Não há empresas cadastradas!")

    def salvar_dados(self, dados: EmpresaCreate):
        try:
            with get_db() as db:
                nova_empresa = EmpresaService.criar_empresa(
                    db=db, empresa_dados=dados
                )
                self.message.definir_mensagem(
                    f"A empresa {nova_empresa.nome_empresa} foi criada com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_EMPRESA] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = (
                e.errors()[0]["msg"]
                if isinstance(e, ValidationError)
                else str(e)
            )
            self.message.definir_mensagem(
                f"Erro ao cadastrar: {msg_erro}", tipo="error"
            )

    def alterar_dados(self, empresa_id: int, dados_empresa: EmpresaUpdate):
        try:
            with get_db() as db:
                empresa_atualizada = EmpresaService.alterar_empresa(
                    db=db, empresa_id=empresa_id, empresa_dados=dados_empresa
                )
                self.message.definir_mensagem(
                    f"A empresa {empresa_atualizada.nome_empresa} foi atualizada com sucesso!",
                    tipo="success",
                )
                self.limpar_dados()
                st.session_state[self.CADASTRO_EMPRESA] = False
                st.rerun()
        except (ValueError, ValidationError) as e:
            msg_erro = (
                e.errors()[0]["msg"]
                if isinstance(e, ValidationError)
                else str(e)
            )
            self.message.definir_mensagem(
                f"Erro ao alterar: {msg_erro}", tipo="error"
            )

    def obter_todas_empresas(self):
        try:
            with get_db() as db:
                return EmpresaService.obter_todas_empresas(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar empresas: {str(e)}", tipo="error"
            )
            return []

    def mudar_tela(self, status: bool):
        st.session_state[self.CADASTRO_EMPRESA] = status
        self.limpar_dados()
        st.rerun()

    def limpar_dados(self):
        """Reseta apenas os dados de edição sem tentar alterar chaves ativas do session_state."""
        st.session_state[self.EDITANDO_EMPRESA] = None