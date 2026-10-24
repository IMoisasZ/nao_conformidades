import streamlit as st
from typing import Literal

TipoMensagem = Literal["success", "error", "warning", "info"]

class MensagemComponent:
    def __init__(self, key_prefix: str = "global"):
        self.key_prefix = key_prefix
        self.key_texto = f"mensagem_texto_{self.key_prefix}"
        self.key_tipo = f"mensagem_tipo_{self.key_prefix}"
        self.lista_tipo_mensagens = ["success", "error", "warning", "info"]

    def definir_mensagem(self, mensagem: str, tipo: TipoMensagem = "info"):
        if tipo not in self.lista_tipo_mensagens:
            st.error("Tipo de mensagem inválido!")
            return

        st.session_state[self.key_texto] = mensagem
        st.session_state[self.key_tipo] = tipo

    def exibir_mensagem(self):
        # ✅ Busca usando as chaves corretas com o prefixo (self.key_texto / self.key_tipo)
        texto = st.session_state.get(self.key_texto)
        tipo = st.session_state.get(self.key_tipo)

        if texto and tipo in self.lista_tipo_mensagens:
            metodo_st = getattr(st, tipo)
            metodo_st(texto)

            # ✅ Limpa as chaves com prefixo para não repetir a mensagem em futuras interações
            st.session_state.pop(self.key_texto, None)
            st.session_state.pop(self.key_tipo, None)