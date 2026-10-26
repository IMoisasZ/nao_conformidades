import streamlit as st

class SelectComponent:
    def __init__(self, label:str="nome_select", options:list=[], value=None, disabled:bool = False, key = None):
        self.label = label
        self.options = options
        self.value = value
        self.disabled = disabled
        self.key = key

    def select(self):
        index_padrao = 0
        if self.value in self.options:
            index_padrao = self.options.index(self.value)
        return st.selectbox(label=self.label, options=self.options, index=index_padrao, disabled=self.disabled, key=self.key)
        