import streamlit as st

from components.header import HeaderComponent
from views.layout_menu import LayoutMenu
from views.layout_rnc import LayoutRnc
from views.pages.setor import SetorPage
from views.layout_principal import LayoutPrincipal


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    # LayoutMenu().renderizar()
    # HeaderComponent(label="Relatório de não conformidade (RNC)").header_rnc()
    # LayoutPrincipal().renderizar()
    app = LayoutPrincipal()
    app.renderizar()
