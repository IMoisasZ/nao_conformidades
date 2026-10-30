"""Módulo de Modelo ORM para Empresas.

Este módulo define a entidade `EmpresaModel` mapeada para a tabela `empresas`
no banco de dados através do SQLAlchemy.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from backend.src.connection.db_connection import Base


class EmpresaModel(Base):
    """Modelo ORM representando a tabela de empresas no banco de dados.

    Attributes:
        id (int): Chave primária autoincrementável da empresa.
        nome_empresa (str): Nome ou razão social da empresa (único e obrigatório, máx. 150 caracteres).
        cnpj (str): Cadastro Nacional da Pessoa Jurídica (único e obrigatório, 14 caracteres).
        ativo (bool): Status do cadastro (padrão True).
        created_at (datetime): Data/hora UTC de criação do registro.
        updated_at (datetime): Data/hora UTC da última atualização do registro.
    """

    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_empresa = Column(String(150), nullable=False, unique=True)
    cnpj = Column(String(14), nullable=False, unique=True)
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
            dict[str, str | int]: Dicionário com id, nome, CNPJ e status formatado.
        """
        return {
            "id": self.id,
            "Empresa": self.nome_empresa,
            "CNPJ": self.cnpj,
            "Ativo": "Sim" if self.ativo else "Não",
        }