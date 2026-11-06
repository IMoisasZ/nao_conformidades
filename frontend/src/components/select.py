import streamlit as st

class SelectComponent:
    def __init__(self, label:str="nome_select", options:list=[], value=None, disabled:bool = False, key = None, default = None, format_func = str):
        self.label = label
        self.options = options
        self.value = value
        self.disabled = disabled
        self.key = key
        self.default = default
        self.format_func = format_func

    def select(self):
        index_padrao = 0
        if self.value in self.options:
            index_padrao = self.options.index(self.value)
        return st.selectbox(label=self.label, options=self.options, index=index_padrao, disabled=self.disabled, key=self.key, format_func=self.format_func)
    
    def multiselect(self):
        return st.multiselect(label=self.label, options=self.options, disabled=self.disabled, key=self.key, default=self.default)
        