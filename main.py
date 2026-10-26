import sys
from backend.src.connection.db_connection import init_db
from pathlib import Path
import streamlit as st

RAIZ = Path(__file__).resolve().parent
FRONTEND_SRC = RAIZ / "frontend" / "src"

if str(RAIZ) not in sys.path:
    sys.path.append(str(RAIZ))

if str(FRONTEND_SRC) not in sys.path:
    sys.path.append(str(FRONTEND_SRC))

from frontend.src.views.layout_principal import LayoutPrincipal


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    try:
        init_db()
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")

    app = LayoutPrincipal()
    app.renderizar()
