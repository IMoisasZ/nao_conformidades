import streamlit as st

class TextAreaComponent:
    def __init__(self, label:str="nome_text_area", disabled:bool=False, value=None):
        self.label = label
        self.disabled = disabled
        self.value = value
        self.text_area = st.text_area(label=self.label, disabled=self.disabled)