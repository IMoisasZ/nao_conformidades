from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.src.connection.db_connection import Base


class UsuarioSetorModel(Base):
    __tablename__ = "usuarios_setores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    setor_id = Column(Integer, ForeignKey("setores.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("usuario_id", "setor_id", name="uq_usuario_setor"),
    )

    usuario = relationship("UsuarioModel", back_populates="setores_vinculados")
    setor = relationship("SetorModel", back_populates="usuarios_vinculados")
    
    @property
    def nome_usuario(self) -> str:
        return self.usuario.nome if self.usuario else ""

    @property
    def nome_setor(self) -> str:
        return self.setor.nome_setor if self.setor else ""
    
    def to_dict(self):
        return {
            "id": self.id,
            "Usuario ID": self.usuario_id,
            "Nome Usuario": self.nome_usuario,
            "Setor ID": self.setor_id,
            "Nome Setor": self.nome_setor
        }