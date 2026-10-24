import streamlit as st

class CheckboxComponent:
    def __init__(self, label:str="nome_checkbox", disabled:bool=False, value:bool=False, key = None):
        self.label = label
        self.disabled = disabled
        self.value = value
        self.key = key

    def checkbox(self):
        return st.checkbox(label=self.label, disabled=self.disabled, value=self.value, key=self.key)