"""Módulo de Definição do Modelo de Usuários.

Este módulo contém a definição da classe enumeradora de perfis de acesso (TipoUsuario)
e o modelo SQLAlchemy (UsuarioModel) referente à tabela `usuarios`.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from backend.src.connection.db_connection import Base


class TipoUsuario(str, enum.Enum):
    """Enumerador dos perfis de permissão e acesso dos usuários no sistema.

    Attributes:
        USUARIO (str): Perfil operacional básico ("Usuário").
        SUPERVISOR (str): Perfil de gestão técnica/setorial ("Supervisor").
        ADMINISTRADOR (str): Perfil de gestão de cadastros e parametrização ("Administrador").
        MASTER (str): Perfil de acesso irrestrito ao sistema ("Master").
    """

    USUARIO = "Usuário"
    SUPERVISOR = "Supervisor"
    ADMINISTRADOR = "Administrador"
    MASTER = "Master"


class UsuarioModel(Base):
    """Modelo ORM representando a tabela de usuários (`usuarios`).

    Esta classe define a estrutura das colunas, tipos de dados, restrições do banco
    de dados, auditoria de criação/atualização e mapeamento de relacionamentos
    muitos-para-muitos (N:N) com os setores de responsabilidade.

    Attributes:
        id (int): Chave primária autoincrementável do usuário.
        codigo (int, optional): Código/matrícula do colaborador. Permite nulo (geração automática sequencial)
            e exige valor único caso preenchido.
        nome (str): Nome completo do usuário.
        email (str, optional): Endereço de e-mail único do colaborador.
        tipo_usuario (TipoUsuario): Perfil de permissão do usuário (mapeado pelo Enum `TipoUsuario`).
        senha (str): Senha de acesso numérica ou alfanumérica de 5 dígitos.
        ativo (bool): Flag que indica se o usuário está ativo (True) ou inativo (False).
        created_at (datetime): Data e hora UTC da criação do registro.
        updated_at (datetime): Data e hora UTC da última alteração do registro.
        setores_vinculados (relationship): Relação 1:N com a tabela intermediária `UsuarioSetorModel`.
            Possui exclusão em cascata.
        setores (relationship): Relação N:N direta com `SetorModel` via tabela pivô `usuarios_setores` (Apenas leitura).
    """

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

    def to_dict(self) -> dict:
        """Converte o objeto `UsuarioModel` em um dicionário formatado.

        Ideal para ser consumido em componentes de interface visual (ex: Dataframes do Streamlit).

        Returns:
            dict: Dicionário contendo os dados do usuário com rótulos amigáveis:
                - "id" (int): Identificador do banco.
                - "Codigo" (int|None): Código/matrícula.
                - "Nome" (str): Nome completo.
                - "Email" (str|None): E-mail.
                - "Tipo usuario" (str): String legível do tipo de usuário.
                - "Senha" (str): Senha cadastrada.
                - "Ativo" (str): Representação textual ("Ativo" ou "Inativo").
        """
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