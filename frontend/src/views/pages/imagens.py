import streamlit as st
import os
from datetime import datetime
from pathlib import Path

from components.input import InputComponent
from components.file_uploader import FileUploaderComponent
from components.button import ButtonComponent
from components.image import ImageComponent

class Imagens:
    def __init__(self):
        self.DADOS_RNC = "dados_rnc"
        if self.DADOS_RNC not in st.session_state:
            st.session_state[self.DADOS_RNC] = {"imagens": []}

    def renderizar(self):
        dados = st.session_state[self.DADOS_RNC]
        if "imagens" not in dados:
            dados["imagens"] = []

        PASTA_UPLOADS = Path(__file__).resolve().parent.parent.parent / "static" / "uploads"
        PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)

        st.subheader("Anexar Imagem da Não Conformidade")

        total_existentes = len(dados["imagens"])

        # 1. Trava do limite máximo de 4 imagens
        if total_existentes >= 4:
            st.warning("⚠️ O limite máximo de 4 imagens para esta RNC já foi atingido.")
        else:
            st.info(f"Imagens cadastradas: **{total_existentes}/4**")

            nome_imagem = InputComponent(
                label="Nome/Descrição da imagem",
                placeholder="Ex: Falta de usinagem...",
                key="input_nome_imagem",
            ).input()

            arquivo_carregado = FileUploaderComponent(
                label="Selecione 1 imagem no seu computador",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=False,
                key="uploader_single"
            ).file_uploader()

            salvar_imagem = ButtonComponent(label="Salvar Imagem", key="btn_salvar").btn()

            if salvar_imagem:
                if not nome_imagem.strip():
                    st.error("Por favor, preencha o nome da imagem antes de salvar.")
                elif not arquivo_carregado:
                    st.error("Por favor, selecione um arquivo de imagem.")
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    extensao = Path(arquivo_carregado.name).suffix
                    
                    nome_sanitizado = "".join(c if c.isalnum() else "_" for c in nome_imagem.strip())
                    nome_arquivo_disco = f"{timestamp}_{nome_sanitizado}{extensao}"
                    caminho_arquivo = PASTA_UPLOADS / nome_arquivo_disco

                    with open(caminho_arquivo, "wb") as f:
                        f.write(arquivo_carregado.getbuffer())

                    novo_item = {
                        "nome": nome_imagem.strip(),
                        "arquivo_disco": nome_arquivo_disco,
                        "tamanho": f"{round(arquivo_carregado.size / 1024, 1)} KB",
                        "caminho": str(caminho_arquivo)
                    }

                    dados["imagens"].append(novo_item)
                    st.success("Imagem salva com sucesso!")
                    st.rerun()

        st.divider()

        # 2. Exibição em grade: 2 imagens lado a lado e a restante abaixo
        if dados["imagens"]:
            st.write("### Imagens Anexadas")
            st.caption("💡 *Passe o mouse ou clique sobre a foto para abri-la em tela cheia com zoom.*")

            lista_imagens = dados["imagens"]

            # Agrupa a lista em pares de 2 itens
            for i in range(0, len(lista_imagens), 2):
                par_imagens = lista_imagens[i:i + 2]
                cols = st.columns(2)  # Cria 2 colunas lado a lado

                for idx_col, item in enumerate(par_imagens):
                    idx_real = i + idx_col  # Índice real do item na lista original

                    with cols[idx_col]:
                        st.markdown(f"#### 📷 {idx_real + 1}. {item['nome']}")
                        
                        # Renderiza a imagem ocupando a largura total da coluna
                        ImageComponent(
                            image=item["caminho"], 
                            use_container_width=True
                        ).img()

                        # Botão de remoção individual abaixo da respectiva foto
                        if ButtonComponent(f"🗑️ Remover", key=f"btn_remover_{idx_real}").btn():
                            caminho_remover = Path(item["caminho"])
                            
                            if caminho_remover.exists():
                                caminho_remover.unlink()

                            dados["imagens"].pop(idx_real)
                            st.success(f"Imagem '{item['nome']}' removida!")
                            nome_imagem = ""
                            st.rerun()