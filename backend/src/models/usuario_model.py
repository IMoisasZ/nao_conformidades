import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from backend.src.connection.db_connection import Base


class TipoUsuario(str, enum.Enum):
    USUARIO = "Usuário"
    SUPERVISOR = "Supervisor"
    ADMINISTRADOR = "Administrador"
    MASTER = "Master"


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(Integer, nullable=True, unique=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True, unique=True)
    tipo_usuario = Column(
        Enum(TipoUsuario, values_callable=lambda obj: [e.value for e in obj])
    )
    senha = Column(String(5), nullable=False)
    ativo = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos N:N
    setores_vinculados = relationship(
        "UsuarioSetorModel", back_populates="usuario", cascade="all, delete-orphan"
    )
    setores = relationship(
        "SetorModel", secondary="usuarios_setores", backref="responsaveis", viewonly=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "Codigo": self.codigo,
            "Nome": self.nome,
            "Email": self.email,
            "Tipo usuario": (
                self.tipo_usuario.value
                if isinstance(self.tipo_usuario, enum.Enum)
                else self.tipo_usuario
            ),
            "Senha": self.senha,
            "Ativo": "Ativo" if self.ativo else "Inativo",
        }