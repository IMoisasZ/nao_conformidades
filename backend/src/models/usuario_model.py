from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.src.connection.db_connection import Base
from datetime import datetime, timezone


class UsuarioModel(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    data_nascimento = Column(DateTime, nullable=False)