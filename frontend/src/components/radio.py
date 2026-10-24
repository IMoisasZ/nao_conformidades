import streamlit as st

class RadioComponent:
    def __init__(self, label:str="nome_radio", options=[], horizontal:bool=False, vars=None):
        self.label = label
        self.options = options
        self.horizontal = horizontal
        self.vars = vars
        self.radio = st.radio(label=self.label, options=self.options, horizontal=self.horizontal)
    