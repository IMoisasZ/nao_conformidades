"""Módulo de Modelo ORM da Entidade Operação.

Este módulo define a estrutura da tabela `operacoes` no banco de dados através do SQLAlchemy ORM,
utilizada para mapear as operações fabris associadas ao apontamento de horas na RNC.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.src.connection.db_connection import Base


class OperacaoModel(Base):
    """Modelo ORM para a tabela `operacoes`.

    Attributes:
        id (int): Chave primária autoincrementável da operação.
        nome_operacao (str): Nome descritivo da operação (único e obrigatório).
        ativo (bool): Status de ativação do cadastro (Padrão: True).
        created_at (datetime): Data e hora UTC da criação do registro.
        updated_at (datetime): Data e hora UTC da última atualização do registro.
    """

    __tablename__ = "operacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_operacao = Column(String(200), nullable=False, unique=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    horas_utilizadas = relationship(
    "HorasUtilizadasModel", back_populates="operacao"
    )

    def to_dict(self) -> dict:
        """Converte a instância do modelo em um dicionário formatado para exibição na interface.

        Returns:
            dict: Dicionário contendo as chaves amigáveis e valores formatados.
        """
        return {
            "ID": self.id,
            "Operação": self.nome_operacao,
            "Ativo": "Ativo" if self.ativo else "Inativo",
        }