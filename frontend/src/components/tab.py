import streamlit as st

class TabComponent:
    def __init__(self, lista_tab=list[str]):
        self.lista_tab = lista_tab

    def tabs(self):
        return st.tabs(tabs=self.lista_tab)