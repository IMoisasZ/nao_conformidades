import streamlit as st
import uuid

class InputComponent:
    def __init__(self, label:str="nome_input", disabled:bool=False, value=None, placeholder:str="", icon:str=None, color:str=None, key:str=None):
        self.label = label
        self.disabled = disabled
        self.value = value
        self.placeholder = placeholder
        self.icon = icon
        self.color = color
        self.key = key if key else f"input_{uuid.uuid4().hex[:8]}"

    def input(self):
        label_visibility = "visible"
        label_color = self.label
        if self.color:
            label_color = st.markdown(f"<p style='color: {self.color}; font-size: 14px; margin-bottom: 6px;'>{self.label}</p>", unsafe_allow_html=True)
            label_visibility = "collapsed"
        else:
            label_color = self.label
        return st.text_input(label=label_color, disabled=self.disabled, value=self.value, placeholder=self.placeholder, icon=self.icon, label_visibility=label_visibility, key=self.key)
