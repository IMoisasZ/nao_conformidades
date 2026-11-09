"""Módulo de Modelo ORM da Entidade Horas Utilizadas.

Este módulo define a estrutura da tabela `horas_utilizadas` no banco de dados através do SQLAlchemy ORM,
mapeando a quantidade de horas apontadas por operação em uma RNC.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from backend.src.connection.db_connection import Base


class HorasUtilizadasModel(Base):
    """Modelo ORM para a tabela `horas_utilizadas`.

    Attributes:
        id (int): Chave primária autoincrementável.
        rnc_id (int): Chave estrangeira para a tabela `rncs`.
        operacao_id (int): Chave estrangeira para a tabela `operacoes`.
        qtde_horas (float): Quantidade de horas apontadas na operação.
        created_at (datetime): Data e hora UTC da criação do registro.
        updated_at (datetime): Data e hora UTC da última atualização do registro.
        rnc (relationship): Relacionamento ORM com o modelo RNCModel.
        operacao (relationship): Relacionamento ORM com o modelo OperacaoModel.
    """

    __tablename__ = "horas_utilizadas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # rnc_id = Column(Integer, ForeignKey("rncs.id"), nullable=False)
    rnc_id = Column(Integer)
    operacao_id = Column(Integer, ForeignKey("operacoes.id"), nullable=False)
    qtde_horas = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # rnc = relationship("RNCModel", backref="horas_utilizadas", lazy="joined")
    operacao = relationship(
    "OperacaoModel", back_populates="horas_utilizadas", lazy="joined"
    )
    
    def to_dict(self) -> dict:
        """Converte a instância do modelo em um dicionário para a interface.

        Returns:
            dict: Dicionário contendo os dados formatados do apontamento.
        """
        return {
            "id": self.id,
            "rnc_id": self.rnc_id,
            "operacao_id": self.operacao_id,
            "qtde_horas": self.qtde_horas,
        }