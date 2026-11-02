"""Módulo de Modelo ORM da Entidade Código de Não Conformidade.

Este módulo define a estrutura da tabela `cadastro_codigo_nc` e a enumeração `TipoNC`,
utilizadas para categorizar e registrar os tipos de não conformidades no banco de dados
através do SQLAlchemy ORM.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String

from backend.src.connection.db_connection import Base


class TipoNC(str, enum.Enum):
    """Enumeração dos tipos/categorias de Não Conformidade.

    Attributes:
        PRODUTIVO (str): Não conformidade relacionada ao processo produtivo.
        PARADA (str): Não conformidade que gera parada de máquina/linha.
        RETRABALHO (str): Não conformidade que exige retrabalho da peça/produto.
    """

    PRODUTIVO = "Produtivo"
    PARADA = "Parada"
    RETRABALHO = "Retrabalho"


class CodigoNC(Base):
    """Modelo ORM para a tabela `cadastro_codigo_nc`.

    Mapeia os códigos e descrições padronizadas das não conformidades,
    permitindo a classificação por tipo de ocorrência e controle de ativação.

    Attributes:
        id (int): Chave primária autoincrementável do código de NC.
        descricao (str): Descrição detalhada da não conformidade (única e obrigatória).
        tipo (TipoNC): Categoria da não conformidade conforme o enum `TipoNC`.
        ativo (bool): Status de ativação do cadastro (Padrão: True).
        created_at (datetime): Data e hora UTC da criação do registro.
        updated_at (datetime): Data e hora UTC da última atualização do registro.
    """

    __tablename__ = "cadastro_codigo_nc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(200), nullable=False, unique=True)
    tipo = Column(
        Enum(TipoNC, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Converte a instância do modelo em um dicionário formatado para exibição na interface.

        Returns:
            dict: Dicionário contendo as chaves amigáveis em português e os valores
            Devidamente formatados.
        """
        return {
            "ID": self.id,
            "Descrição": self.descricao,
            "Tipo": (
                self.tipo.value
                if isinstance(self.tipo, enum.Enum)
                else self.tipo
            ),
            "Ativo": "Ativo" if self.ativo else "Inativo",
        }