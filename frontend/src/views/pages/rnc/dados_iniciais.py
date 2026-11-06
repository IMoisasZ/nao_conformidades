import streamlit as st

from components.select import SelectComponent
from components.input import InputComponent
from components.radio import RadioComponent
from components.button import ButtonComponent
from components.checkbox import CheckboxComponent
from components.text_area import TextAreaComponent
from components.title_page import TitlePages

from backend.src.connection.db_connection import get_db
from backend.src.services.codigo_nc_service import CodigoNCService
from backend.src.services.setor_service import SetorService
from backend.src.services.cliente_service import ClienteService
from backend.src.services.fornecedor_service import FornecedorService

from views.pages.rnc.horas_utilizadas import HorasUtilizadas

class DadosInciais:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        self.VIEW_ATIVA = "view_ativa"
        self.CADASTRAR_HRS_UTILIZADAS = "cadastrar_hrs_utilizadas"

        if self.CADASTRAR_HRS_UTILIZADAS not in st.session_state:
            st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = False
    
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {
                "numero_rnc": "",
                "data_rnc": "",
                "status_rnc": "",
                "codigo_nc": "",
                "origem": "",
                "setor": "",
                "fornecedor":"",
                "cliente":"",
                "hrs_utilizadas": "",
                "qtde_rejeitada": "",
                "nf": "",
                "op": "",
                "di":"",
                "os": "",
                "oc": "",
                "di_informacoes": "",
                "destinatario_id": "",
                "descricao_nc": "",
                "imagens": [],
                "disposicao_nc": "",
                "numero_concessao": "",
                "descricao_disposicao": "",
                "causa_nc":"",
                "responsavel_id": "",
                "data_causa_nc":"" 
            }

            if self.VIEW_ATIVA not in st.session_state:
                st.session_state[self.VIEW_ATIVA] = "cadastro"

    def renderizar(self):
        if st.session_state.get(self.CADASTRAR_HRS_UTILIZADAS):
            self.horas_utilizadas()
        else:
            self.cadastro_view()

    def cadastro_view(self):
        dados = st.session_state[self.DADOS_RNC]
        
        codigo_nc_col, descricao_codigo_nc_col = st.columns([2,8])

        with codigo_nc_col:
            codigos_nc = self.obter_todos_codigos_apontamento()
            codigo_nc = SelectComponent(
                label="Codigo não conformidade", 
                options=[item.id for item in codigos_nc], 
                value=dados.get("codigo_nc"), 
                format_func=lambda id_item: next(
                    f"{c.id}" for c in codigos_nc if c.id == id_item
                ), key="select_codigo_rnc").select()
            codigo_nc_obj = next(
                (item for item in codigos_nc if item.id == codigo_nc), None
            )
            dados["codigo_nc"] = codigo_nc
        with descricao_codigo_nc_col:
            descricao_nc = InputComponent(label="Descrição Código Não Conformidade", placeholder="Descrição do código da não conformidade", disabled=True, value=codigo_nc_obj.descricao if codigo_nc_obj else "").input()

        st.divider()
        origem_col, setor_col, fornecedor_col, cliente_col = st.columns(4)
        with origem_col:
            origem = RadioComponent(label="Origem", options=["Setor", "Fornecedor", "Cliente"], horizontal=True, vars=dados.get("origem")).radio
            dados["origem"] = origem
        with setor_col:
            setores = self.obter_todos_setores()
            setor = SelectComponent(label="Setor", options=[item.nome_setor for item in setores] if origem == "Setor" else [], disabled=True if origem != "Setor" else False, value=dados.get("codigo_nc")).select()
            dados["setor"] = setor
        with fornecedor_col:
            fornecedores = self.obter_todos_fornecedores()
            fornecedor = SelectComponent(label="Fornecedor", options=[item.nome_fornecedor for item in fornecedores] if origem == "Fornecedor" else [], disabled=True if origem != "Fornecedor" else False, value=dados.get("fornecedor")).select()
            dados["fornecedor"] = fornecedor
        with cliente_col:
            clientes = self.obter_todos_clientes()
            cliente = SelectComponent(label="Cliente", options=[item.nome_cliente for item in clientes] if origem == "Cliente" else [], disabled=True if origem != "Cliente" else False, value=dados.get("cliente")).select()
            dados["cliente"] = cliente
        st.divider()

        hrs_utilizadas_col, btn, qtde_rejeitada_col, espaco = st.columns([2,2,2,8], vertical_alignment="bottom")
        with hrs_utilizadas_col:
            hrs_utilizadas = InputComponent(label="Horas utilizadas", disabled=True, icon="⏱", placeholder="", value=dados.get("hrs_utilizadas")).input()
            dados["hrs_utilizadas"] = hrs_utilizadas
        with btn: 
            ButtonComponent(label="Hrs utilizadas", icon="⏱", width="stretch", onclick=self.abrir_modal_hrs_utilizadas).btn()
        with qtde_rejeitada_col:
            qtde_rejeitada = InputComponent(label="Qtde rejeitada", value=dados.get("qtde_rejeitada")).input()
            dados["qtde_rejeitada"] = qtde_rejeitada

        st.divider()
        st.write("Documentos:")
        chk_nf_col, chk_op_col, chk_di_col, chk_os_col, chk_oc_col = st.columns(5)
        with chk_nf_col:
            chk_nf = CheckboxComponent(label="Nota fiscal").checkbox()
            nf = InputComponent(label="Nota fiscal", placeholder="Informe o numero da NF...", disabled=False if chk_nf else True, value=dados.get("nf")).input()
            dados["nf"] = nf
        with chk_op_col:    
            chk_op = CheckboxComponent(label="OP").checkbox()
            op = InputComponent(label="OP", placeholder="Informe o numero da OP...", disabled=False if chk_op else True, value=dados.get("op")).input()
            dados["op"] = op
        with chk_di_col:
            chk_di = CheckboxComponent(label="DI").checkbox()
            di = InputComponent(label="DI", placeholder="Informe o numero da DI...", disabled=False if chk_di else True, value=dados.get("di")).input()
            dados["di"] = di
        with chk_os_col:    
            chk_os = CheckboxComponent(label="OS").checkbox()
            os = InputComponent(label="OS", placeholder="Informe o numero da OS...", disabled=False if chk_os else True, value=dados.get("os")).input()
            dados["os"] = os
        with chk_oc_col:    
            chk_oc = CheckboxComponent(label="OC").checkbox()
            oc = InputComponent(label="OC", placeholder="Informe o numero da OC...", disabled=False if chk_oc else True, value=dados.get("oc")).input()
            dados["oc"] = oc
        di_informacoes = TextAreaComponent(label="Informações da DI", disabled=False if chk_di else True, value=dados.get("di_informacoes")).text_area
        dados["di_informacoes"] = di_informacoes

        destinatario = SelectComponent(label="Destinatário", options=["Moisés", "Gustavo", "Robson", "João Bautista", "Edmar", "Nunes"], value=dados.get("destinatario_id")).select()
        dados["destinatario_id"] = destinatario

        st.divider()

    def obter_todos_codigos_apontamento(self):
        try:
            with get_db() as db:
                codigos_nc = CodigoNCService.obter_todos_codigos_nc(db=db)
                return codigos_nc
        except Exception as e:
            raise e

    def obter_todos_setores(self):
        try:
            with get_db() as db:
                setores = SetorService.obter_todos_setores(db=db)
                return setores
        except Exception as e:
                    raise e

    def obter_todos_fornecedores(self):
        try:
            with get_db() as db:
                fornecedores = FornecedorService.obter_todos_fornecedores(db=db)
                return fornecedores
        except Exception as e:
            raise e    

    def obter_todos_clientes(self):
        try:
            with get_db() as db:
                clientes = ClienteService.obter_todos_clientes(db=db)
                return clientes
        except Exception as e:
            raise e      

    def hrs_utilizadas(self):        
        st.session_state[self.CADASTRAR_HRS_UTILIZADAS] = True

    def abrir_modal_hrs_utilizadas(self):
        HorasUtilizadas().renderizar()
        
        





