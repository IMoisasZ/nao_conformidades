import streamlit as st

from components.mensagem import MensagemComponent
from components.divider import Divider

from backend.src.connection.db_connection import get_db
from backend.src.services.operacao_service import OperacaoService

class HorasUtilizadas:
    def __init__(self):
        self.CADASTRAR_HRS_UTILIZADAS = "cadastrar_hrs_utilizadas"
        self.EDITANDO_HRS_UTILIZADAS = "editando_hrs_utilizadas"
        self.message = MensagemComponent()

        if self.CADASTRAR_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = True

        if self.EDITANDO_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.EDITANDO_HRS_UTILIZADAS] = None

    @st.dialog("Horas Utilizadas na RNC")
    def renderizar(self):
        self.message.exibir_mensagem()
        self.cadastro_view()

    def cadastro_view(self):
        editando = st.session_state.get(self.EDITANDO_HRS_UTILIZADAS)
        is_edicao = editando is not None
        
        if is_edicao:
            horas_utilizadas_dados = editando.get("dados")
            
            if hasattr(horas_utilizadas_dados, "id"):
                id_padrao = horas_utilizadas_dados.id
                rnc_id_padrao = getattr(horas_utilizadas_dados, "rnc_id") or None
                operacao_id_padrao = getattr(horas_utilizadas_dados, "operacao_id", "" ) or None
                qtde_horas_padrao = getattr(horas_utilizadas_dados, "qtde_horas") or None
            elif isinstance(horas_utilizadas_dados, dict):
                id_padrao = horas_utilizadas_dados.get("id") or horas_utilizadas_dados.get("ID")
                rnc_id_padrao = horas_utilizadas_dados.get("rnc_id") or None
                operacao_id_padrao = horas_utilizadas_dados.get("operacao_id") or ""
            else:
                id_padrao = None
                is_edicao = False
                rnc_id_padrao = None
                operacao_id_padrao = None
                qtde_horas_padrao = None
        else:
            id_padrao = None
            rnc_id_padrao = None
            operacao_id_padrao = None
            qtde_horas_padrao = None
        
        col_operacao, col_qtde_horas = st.columns([8,2])
        with col_operacao:    
            operacoes = self.obter_todas_operacoes()
            idx_operacao = self.obter_todas_operacoes.index(operacao_id_padrao) if operacao_id_padrao in operacoes else 0
            operacao = st.selectbox(label="Operação", options=[item.nome_operacao for item in operacoes], key="select_operacao_id", index=idx_operacao)
        with col_qtde_horas:
            qtde_horas = st.text_input(label="Qtde horas", key="input_qtde_horas")

        Divider(color="gray").divider()
        

        col_btn_incluir, col_btn_remover = st.columns(2)
        with col_btn_incluir:
            st.button(label="Incluir horas", width="stretch", type="primary")
        with col_btn_remover:
            st.button(label="Remover horas", width="stretch", type="secondary", disabled=not is_edicao)
            
        Divider(color="gray").divider()
        
        self.lista_view()
            
    def lista_view(self):
        horas_utilizadas = self.obter_horas_utilizadas(rnc_id=None)
        
        if horas_utilizadas:
            evento_selecao = st.dataframe(data=
            horas_utilizadas, on_select="rerun", hide_index=True, selection_mode="single-row")
            linha_selecionada = evento_selecao.get("selection", {}).get("rows", [])
            
            if linha_selecionada:
                indice = linha_selecionada[0]
                horas_utiizadas_selecionada = horas_utilizadas[indice]
                st.session_state[self.EDITANDO_HRS_UTILIZADAS] = {
                    "idnice": indice,
                    "dados": horas_utiizadas_selecionada
                }
        else:
            st.write(" #### Não há horas utilizadas para RNC!")        
            
    def obter_todas_operacoes(self):
        try:
            with get_db() as db:
                operacoes = OperacaoService.obter_todas_operacoes(db=db,)
                return operacoes
        except Exception as e:
            self.message.definir_mensagem(f"Erro ao carregar operações: {str(e)}", tipo="error")
            return []
        
    def obter_horas_utilizadas(self, rnc_id:int):
        pass
        
    