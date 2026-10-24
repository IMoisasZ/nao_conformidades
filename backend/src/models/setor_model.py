from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.src.connection.db_connection import Base
from datetime import datetime, timezone

class SetorModel(Base):
    __tablename__ = "setores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_setor = Column(String(150), nullable=False, unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "Setor": self.nome_setor,
            "Ativo": "Ativo" if self.ativo else "Inativo"
        }