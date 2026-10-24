from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.src.connection.db_connection import Base
from datetime import datetime, timezone

class EmpresaModel(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_empresa = Column(String(150), nullable=False, unique=True)
    cnpj = Column(String(14), nullable=False, unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "Empresa": self.nome_empresa,
            "CNPJ": self.cnpj,
            "Ativo": "Sim" if self.ativo else "Não"
        }