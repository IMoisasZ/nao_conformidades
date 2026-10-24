import streamlit as st

class Divider:
    def __init__(self, color:str="orange"):
        self.color = color
        
    def divider(self):
        return st.markdown(
            f"""
                <div style="border-bottom: 1px solid {self.color}; width: 100%; margin-bottom: 10px">
                </div>
            """,
            unsafe_allow_html=True
        )