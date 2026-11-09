"""Módulo de Schemas Pydantic da Entidade Horas Utilizadas.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
atualização e serialização dos dados referentes aos apontamentos de horas por operação na RNC.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HorasUtilizadasCreate(BaseModel):
    """Schema Pydantic para criação de novos apontamentos de horas.

    Attributes:
        rnc_id (int): Identificador da RNC associada.
        operacao_id (int): Identificador da operação realizada.
        qtde_horas (float): Quantidade de horas apontadas (deve ser maior que zero).
    """

    rnc_id: int = Field(..., gt=0, description="ID da RNC")
    operacao_id: int = Field(..., gt=0, description="ID da operação")
    qtde_horas: float = Field(..., gt=0, description="Qtde de horas utilizadas")


class HorasUtilizadasUpdate(BaseModel):
    """Schema Pydantic para atualização de apontamentos de horas existentes.

    Attributes:
        id (int): Identificador único do registro de utilização de horas.
        operacao_id (Optional[int]): Novo ID da operação (opcional).
        qtde_horas (Optional[float]): Nova quantidade de horas utilizadas (opcional).
    """

    id: int = Field(..., description="ID do registro de utilização de horas")
    operacao_id: Optional[int] = Field(None, gt=0, description="ID da operação")
    qtde_horas: Optional[float] = Field(None, gt=0, description="Qtde horas utilizadas")


class HorasUtilizadasResponse(BaseModel):
    """Schema Pydantic para serialização e resposta dos dados de Horas Utilizadas.

    Attributes:
        id (int): Chave primária do apontamento.
        rnc_id (int): ID da RNC associada.
        operacao_id (int): ID da operação realizada.
        nome_operacao (Optional[str]): Nome descritivo da operação para exibição na UI.
        qtde_horas (float): Quantidade de horas lançadas.
        created_at (Optional[datetime]): Data e hora UTC da criação do registro.
    """

    id: int
    rnc_id: int
    operacao_id: int
    nome_operacao: Optional[str] = None
    qtde_horas: float
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)