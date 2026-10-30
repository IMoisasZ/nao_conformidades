"""Módulo de Modelo ORM para Clientes.

Este módulo define a entidade `ClienteModel` mapeada para a tabela `clientes`
no banco de dados através do SQLAlchemy.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from backend.src.connection.db_connection import Base


class ClienteModel(Base):
    """Modelo ORM representando a tabela de clientes no banco de dados.

    Attributes:
        id (int): Chave primária autoincrementável do cliente.
        nome_cliente (str): Nome do cliente (único e obrigatório, máx. 150 caracteres).
        ativo (bool): Status do cadastro (padrão True).
        created_at (datetime): Data/hora UTC de criação do registro.
        updated_at (datetime): Data/hora UTC da última atualização do registro.
    """

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_cliente = Column(String(150), nullable=False, unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict[str, str | int]:
        """Converte o objeto da entidade em um dicionário estruturado.

        Útil para formatação em tabelas e exibição no Streamlit.

        Returns:
            dict[str, str | int]: Dicionário com id, nome legível e status em texto.
        """
        return {
            "id": self.id,
            "Cliente": self.nome_cliente,
            "Ativo": "Ativo" if self.ativo else "Inativo",
        }