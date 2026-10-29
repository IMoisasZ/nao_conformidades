import streamlit as st

class TabComponent:
    def __init__(self, lista_tab=list[str], key:str = None):
        self.lista_tab = lista_tab
        self.key = key

    def tabs(self):
        return st.tabs(tabs=self.lista_tab, key=self.key)