"""Componente de Interface para Gestão de Horas Utilizadas na RNC."""

from typing import Any, Dict, List, Optional
import streamlit as st

from backend.src.connection.db_connection import get_db
from backend.src.services.horas_utilizadas_service import HorasUtilizadasService
from backend.src.services.operacao_service import OperacaoService
from components.divider import Divider
from components.mensagem import MensagemComponent


class HorasUtilizadas:
    """Componente de interface para gestão de Horas Utilizadas."""

    def __init__(self, rnc_id: Optional[int] = None):
        self.rnc_id = rnc_id
        self.CADASTRAR_HRS_UTILIZADAS = "cadastrar_hrs_utilizadas"
        self.EDITANDO_HRS_UTILIZADAS = "editando_hrs_utilizadas"
        self.TABELA_HORAS_UTILIZADAS = "tabela_horas_utilizadas"
        self.TOTAL_HORAS_UTILIZADAS = "total_horas_utilizadas"
        self.message = MensagemComponent()

        if self.CADASTRAR_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = True

        if self.EDITANDO_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.EDITANDO_HRS_UTILIZADAS] = None

        if self.TABELA_HORAS_UTILIZADAS not in st.session_state:
            st.session_state[self.TABELA_HORAS_UTILIZADAS] = []

        if self.TOTAL_HORAS_UTILIZADAS not in st.session_state:
            st.session_state[self.TOTAL_HORAS_UTILIZADAS] = 0.0

    def renderizar(self):
        """Renderiza a visualização do componente de Horas Utilizadas."""
        self.message.exibir_mensagem()
        self.cadastro_view()

    def _limpar_estado_formulario(self):
        """Reseta o estado de edição e remove as chaves vinculadas aos widgets."""
        st.session_state[self.EDITANDO_HRS_UTILIZADAS] = None
        st.session_state.pop("input_qtde_horas", None)
        st.session_state.pop("select_operacao_id", None)

    def cadastro_view(self):
        # 1. Carrega operações e monta o mapeamento
        operacoes = self.obter_todas_operacoes()
        mapa_operacoes = (
            {
                op.id: getattr(op, "nome_operacao", getattr(op, "nome", f"Operação {op.id}"))
                for op in operacoes
            }
            if operacoes
            else {}
        )
        lista_op_ids = list(mapa_operacoes.keys())

        # 2. Verifica o estado de edição atual
        editando = st.session_state.get(self.EDITANDO_HRS_UTILIZADAS)
        is_edicao = editando is not None

        id_padrao = None
        operacao_id_padrao = None

        if is_edicao:
            horas_utilizadas_dados = editando.get("dados", {})
            if hasattr(horas_utilizadas_dados, "id"):
                id_padrao = horas_utilizadas_dados.id
                operacao_id_padrao = getattr(horas_utilizadas_dados, "operacao_id", None)
            elif isinstance(horas_utilizadas_dados, dict):
                id_padrao = horas_utilizadas_dados.get("id") or horas_utilizadas_dados.get("ID")
                operacao_id_padrao = horas_utilizadas_dados.get("operacao_id")

        idx_operacao = (
            lista_op_ids.index(operacao_id_padrao)
            if operacao_id_padrao in lista_op_ids
            else 0
        )

        # 3. Garante inicialização limpa da chave do text_input ANTES da criação do widget
        if "input_qtde_horas" not in st.session_state:
            st.session_state["input_qtde_horas"] = ""

        # 4. Formulário principal de cadastro/edição
        with st.form("horas_utilizadas_form", clear_on_submit=False):
            col_operacao, col_qtde_horas = st.columns([8, 2])
            with col_operacao:
                operacao_selecionada_id = st.selectbox(
                    label="Operação",
                    options=lista_op_ids,
                    format_func=lambda op_id: mapa_operacoes.get(op_id, f"Operação {op_id}"),
                    key="select_operacao_id",
                    index=idx_operacao if lista_op_ids else 0,
                )

            with col_qtde_horas:
                # O widget lê diretamente a chave 'input_qtde_horas' de st.session_state
                qtde_horas = st.text_input(
                    label="Qtde horas",
                    key="input_qtde_horas",
                )

            Divider(color="gray").divider()

            label_btn = "Alterar" if is_edicao else "Incluir horas"
            btn_incluir_editar_horas = st.form_submit_button(
                label=label_btn, use_container_width=True, type="primary"
            )

        # 5. Botões de exclusão (fora do formulário)
        if is_edicao:
            col_btn_remover_selecao, col_btn_remover_todos = st.columns(2)
            with col_btn_remover_selecao:
                btn_remover_selecao = st.button(
                    label="Remover hora selecionada",
                    use_container_width=True,
                    type="secondary",
                )
            with col_btn_remover_todos:
                btn_remover_todas = st.button(
                    label="Remover todas as horas",
                    use_container_width=True,
                    type="primary",
                )

            if btn_remover_selecao:
                self.remover_selecao(editando=editando)

            if btn_remover_todas:
                self.remover_todas()

        # 6. Renderização da Tabela de Registros
        self.lista_view(mapa_operacoes=mapa_operacoes)

        Divider(color="gray").divider()

        # Total de horas acumulado
        total = st.session_state.get(self.TOTAL_HORAS_UTILIZADAS, 0.0)
        if total > 0.0:
            st.markdown(f"**Total de Horas Utilizadas na RNC:** `{total:.2f} h`")
            Divider(color="gray").divider()

        # 7. Trata a submissão do formulário
        if btn_incluir_editar_horas:
            try:
                qtde_float = float(qtde_horas.replace(",", "."))
                dados_horas_utilizadas = {
                    "id": id_padrao,
                    "operacao_id": operacao_selecionada_id,
                    "nome_operacao": mapa_operacoes.get(operacao_selecionada_id, ""),
                    "qtde_horas": qtde_float,
                }
                self.salvar_dados(
                    dados_horas_utilizadas=dados_horas_utilizadas,
                    is_edicao=is_edicao,
                )
            except ValueError:
                self.message.definir_mensagem(
                    "Informe um valor numérico válido para a quantidade de horas.",
                    tipo="warning",
                )
                st.rerun()

    def lista_view(self, mapa_operacoes: Dict[int, str]):
        """Carrega e exibe a lista de horas na tabela com suporte a seleção de linha."""
        horas_exibicao: List[Dict[str, Any]] = []

        if self.rnc_id:
            horas_banco = self.obter_horas_utilizadas(rnc_id=self.rnc_id)
            for item in horas_banco:
                op_id = getattr(item, "operacao_id", None)
                horas_exibicao.append(
                    {
                        "id": getattr(item, "id", None),
                        "operacao_id": op_id,
                        "Operação": mapa_operacoes.get(op_id, f"ID {op_id}"),
                        "Qtde Horas": getattr(item, "qtde_horas", 0.0),
                        "_objeto_original": item,
                    }
                )
        else:
            for idx, item in enumerate(st.session_state[self.TABELA_HORAS_UTILIZADAS]):
                op_id = item.get("operacao_id")
                horas_exibicao.append(
                    {
                        "indice_temp": idx,
                        "operacao_id": op_id,
                        "Operação": item.get(
                            "nome_operacao", mapa_operacoes.get(op_id, "")
                        ),
                        "Qtde Horas": float(item.get("qtde_horas", 0.0)),
                        "_objeto_original": item,
                    }
                )

        self.calcular_total_horas_utilizadas([row["_objeto_original"] for row in horas_exibicao])

        if horas_exibicao:
            dados_df = [
                {"Operação": row["Operação"], "Qtde Horas": row["Qtde Horas"]}
                for row in horas_exibicao
            ]

            evento_selecao = st.dataframe(
                data=dados_df,
                on_select="rerun",
                hide_index=True,
                selection_mode="single-row",
                use_container_width=True,
            )

            linhas_selecionadas = evento_selecao.get("selection", {}).get("rows", [])

            if linhas_selecionadas:
                idx_selecionado = linhas_selecionadas[0]
                item_selecionado = horas_exibicao[idx_selecionado]

                novo_estado = {
                    "indice": idx_selecionado,
                    "dados": item_selecionado["_objeto_original"],
                }

                if st.session_state.get(self.EDITANDO_HRS_UTILIZADAS) != novo_estado:
                    st.session_state[self.EDITANDO_HRS_UTILIZADAS] = novo_estado

                    # Extrai a quantidade de horas selecionada
                    dados = item_selecionado["_objeto_original"]
                    valor_qtde = (
                        getattr(dados, "qtde_horas", "")
                        if hasattr(dados, "qtde_horas")
                        else dados.get("qtde_horas", "")
                    )

                    # Removemos as chaves dos widgets e forçamos o rerun.
                    # No próximo rerun (que inicia ANTES do st.form), o valor correto é injetado.
                    st.session_state.pop("input_qtde_horas", None)
                    st.session_state.pop("select_operacao_id", None)
                    st.session_state["input_qtde_horas"] = str(valor_qtde)
                    st.rerun()
            else:
                if st.session_state.get(self.EDITANDO_HRS_UTILIZADAS) is not None:
                    self._limpar_estado_formulario()
                    st.rerun()
        else:
            st.info("Não há horas utilizadas cadastradas para esta RNC.")

    def obter_todas_operacoes(self) -> list:
        try:
            with get_db() as db:
                return OperacaoService.obter_todas_operacoes(db=db)
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar operações: {str(e)}", tipo="error"
            )
            return []

    def obter_horas_utilizadas(self, rnc_id: int) -> list:
        try:
            with get_db() as db:
                return HorasUtilizadasService.obter_todas_horas_utilizadas(
                    db=db, rnc_id=rnc_id
                )
        except Exception as e:
            self.message.definir_mensagem(
                f"Erro ao carregar horas da RNC: {str(e)}", tipo="error"
            )
            return []

    def calcular_total_horas_utilizadas(self, dados_horas: List[Any]):
        if not dados_horas:
            st.session_state[self.TOTAL_HORAS_UTILIZADAS] = 0.0
            return

        total = 0.0
        for item in dados_horas:
            if hasattr(item, "qtde_horas"):
                total += float(getattr(item, "qtde_horas", 0.0))
            elif isinstance(item, dict):
                total += float(item.get("qtde_horas", 0.0))

        st.session_state[self.TOTAL_HORAS_UTILIZADAS] = round(total, 2)

    def salvar_dados(self, dados_horas_utilizadas: dict, is_edicao: bool):
        if self.rnc_id:
            try:
                with get_db() as db:
                    if is_edicao and dados_horas_utilizadas.get("id"):
                        from backend.src.schemas.horas_utilizadas_schema import (
                            HorasUtilizadasUpdate,
                        )

                        schema_update = HorasUtilizadasUpdate(
                            id=dados_horas_utilizadas["id"],
                            operacao_id=dados_horas_utilizadas["operacao_id"],
                            qtde_horas=dados_horas_utilizadas["qtde_horas"],
                        )
                        HorasUtilizadasService.alterar_horas_utilizadas(
                            db=db,
                            rnc_id=self.rnc_id,
                            id_horas_utilizadas=dados_horas_utilizadas["id"],
                            dados_horas_utilizadas=schema_update,
                        )
                    else:
                        from backend.src.schemas.horas_utilizadas_schema import (
                            HorasUtilizadasCreate,
                        )

                        schema_create = HorasUtilizadasCreate(
                            rnc_id=self.rnc_id,
                            operacao_id=dados_horas_utilizadas["operacao_id"],
                            qtde_horas=dados_horas_utilizadas["qtde_horas"],
                        )
                        HorasUtilizadasService.criar_horas_utilizadas(
                            db=db, dados_horas_utilizadas=[schema_create]
                        )
                        db.commit()

                self._limpar_estado_formulario()
                self.message.definir_mensagem(
                    "Registro gravado com sucesso!", tipo="success"
                )
                st.rerun()
            except Exception as e:
                self.message.definir_mensagem(
                    f"Erro ao salvar horas no banco: {str(e)}", tipo="error"
                )
        else:
            if is_edicao:
                editando = st.session_state.get(self.EDITANDO_HRS_UTILIZADAS)
                idx = editando.get("indice")
                st.session_state[self.TABELA_HORAS_UTILIZADAS][idx] = dados_horas_utilizadas
            else:
                st.session_state[self.TABELA_HORAS_UTILIZADAS].append(
                    dados_horas_utilizadas
                )

            self._limpar_estado_formulario()
            st.rerun()

    def remover_selecao(self, editando: dict):
        if self.rnc_id:
            dados_item = editando.get("dados", {})
            hora_id = getattr(dados_item, "id", None) or dados_item.get("id")
            if hora_id:
                try:
                    with get_db() as db:
                        HorasUtilizadasService.remover_horas_utilizadas_pelo_id(
                            db=db, id_horas_utilizadas=hora_id
                        )
                    self._limpar_estado_formulario()
                    self.message.definir_mensagem(
                        "Registro removido com sucesso!", tipo="success"
                    )
                    st.rerun()
                except Exception as e:
                    self.message.definir_mensagem(
                        f"Erro ao remover registro: {str(e)}", tipo="error"
                    )
        else:
            idx = editando.get("indice")
            if idx is not None and idx < len(st.session_state[self.TABELA_HORAS_UTILIZADAS]):
                st.session_state[self.TABELA_HORAS_UTILIZADAS].pop(idx)

            self._limpar_estado_formulario()
            st.rerun()

    def remover_todas(self):
        if self.rnc_id:
            try:
                with get_db() as db:
                    HorasUtilizadasService.remover_todas_horas_utilizadas(
                        db=db, rnc_id=self.rnc_id
                    )
                self._limpar_estado_formulario()
                self.message.definir_mensagem(
                    "Todos os registros foram removidos com sucesso!", tipo="success"
                )
                st.rerun()
            except Exception as e:
                self.message.definir_mensagem(
                    f"Erro ao remover todos os registros: {str(e)}", tipo="error"
                )
        else:
            st.session_state[self.TABELA_HORAS_UTILIZADAS] = []
            self._limpar_estado_formulario()
            st.rerun()