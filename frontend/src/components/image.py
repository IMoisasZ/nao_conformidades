import streamlit as st

class ImageComponent:
    def __init__(self, image:str=None, use_container_width:bool=True):
        self.image = image
        self.use_container_width = use_container_width

    def img(self):
        return st.image(
            image=self.image, 
            use_container_width=self.use_container_width
        )