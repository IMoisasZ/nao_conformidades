from sqlalchemy import Column, Integer, String, DateTime, Boolean
from backend.src.connection.db_connection import Base
from datetime import datetime, timezone

class ClienteModel(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_cliente = Column(String(150), nullable=True, unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda:datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))

    def ti_dict(self):
        return {
            "id": self.id,
            "Cliente": self.nome_cliente,
            "Ativo": "Ativo" if self.ativo else "Inativo"
        }
    