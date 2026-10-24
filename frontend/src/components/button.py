import streamlit as st
import uuid

class ButtonComponent:
    def __init__(self, label:str="nome_btn", icon:str=None, width="stretch", onclick=None, args = None, disabled:bool=False, key:str=None):
        self.label = label
        self.icon = icon
        self.width = width
        self.onclick = onclick
        self.args = args
        self.disabled = disabled
        self.key = key if key else f"input_{uuid.uuid4().hex[:8]}"
    def btn(self):
        return st.button(label=self.label, icon=self.icon, width=self.width, on_click=self.onclick, args=self.args, disabled=self.disabled, key=self.key)