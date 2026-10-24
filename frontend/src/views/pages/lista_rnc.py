import streamlit as st

from components.button import ButtonComponent

class ListaRnc:
    def __init__(self):
        self.VIEW_ATIVA = "view_ativa"
        if self.VIEW_ATIVA not in st.session_state:
            st.session_state[self.VIEW_ATIVA] = "lista"

    def renderizar(self):
        st.write("## Lista RNC")
        ButtonComponent(label="Cadastro RNC", onclick=self.mudar_tela).btn()

        data_table = [{
            "Data":"",
            "RNC":"",
            "Emitente":"",
            "Setor": "",
            "Fornecedor": "",
            "Cliente": "",
            "Hrs Utilizadas": "",
            "Qtde Rejietada": "",
            "NF": "",
            "OP": "",
            "DI": "",
            "OS": "",
            "OC": "",
            "Destinatário": "",
            "Descrição Não Conformidade":"",
            "Disposição Não Conformidade": "",
            "Descrição da Disposição da Não Conformidade": "",
            "Status": ""
        }]
        st.dataframe(data=data_table)

    def mudar_tela(self):
        st.session_state[self.VIEW_ATIVA] = "cadastro"
        st.rerun()
