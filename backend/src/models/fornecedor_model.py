"""Módulo de Modelo ORM para Fornecedores.

Este módulo define a entidade `FornecedorModel` mapeada para a tabela `fornecedores`
no banco de dados através do SQLAlchemy.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from backend.src.connection.db_connection import Base


class FornecedorModel(Base):
    """Modelo ORM representando a tabela de fornecedores no banco de dados.

    Attributes:
        id (int): Chave primária autoincrementável do fornecedor.
        nome_fornecedor (str): Nome ou razão social do fornecedor (único e obrigatório, máx. 150 caracteres).
        ativo (bool): Status do cadastro (padrão True).
        created_at (datetime): Data/hora UTC de criação do registro.
        updated_at (datetime): Data/hora UTC da última atualização do registro.
    """

    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_fornecedor = Column(String(150), nullable=False, unique=True)
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
            "Fornecedor": self.nome_fornecedor,
            "Ativo": "Ativo" if self.ativo else "Inativo",
        }