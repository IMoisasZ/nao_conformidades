import streamlit as st
import uuid

class FileUploaderComponent:
    def __init__(self, label:str="Selecione 1 imagem no seu computador", type = ["png", "jpg", "jpeg"], accept_multiple_files:bool=False, key:str=None):
        self.label = label
        self.type = type
        self.accept_multiple_files = accept_multiple_files
        self.key = key if key else f"input_{uuid.uuid4().hex[:8]}"

    def file_uploader(self):
        return st.file_uploader(
                label=self.label,
                type=self.type,
                accept_multiple_files=self.accept_multiple_files,
                key=self.key
            )