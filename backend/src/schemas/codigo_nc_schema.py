"""Módulo de Schemas Pydantic da Entidade Código de Não Conformidade.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes aos códigos de não
conformidade na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.src.models.codigo_nc_model import TipoNC
from backend.src.utils.tratamento_dados_util import TratamentoDados


class CodigoNCCreate(BaseModel):
    """Schema Pydantic para criação de novos códigos de não conformidade.

    Attributes:
        min_length_descricao (ClassVar[int]): Comprimento mínimo exigido para a descrição (5 caracteres).
        descricao (str): Descrição detalhada do código de NC (entre 5 e 200 caracteres).
        tipo (TipoNC): Categoria do código de NC (Enum `TipoNC`).
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_descricao: ClassVar[int] = 5

    descricao: str = Field(
        ...,
        min_length=min_length_descricao,
        max_length=200,
        description="Descrição do código de não conformidade!",
    )
    tipo: TipoNC = Field(..., description="Tipo de código de não conformidade")
    ativo: bool = True

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v: str) -> str:
        """Valida e sanitiza a descrição informada para o código de NC.

        Args:
            v (str): Valor bruto informado para a descrição.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades).

        Raises:
            ValueError: Se a descrição não atender aos critérios mínimos de tamanho.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="descrição do código da não conformidade",
            min_length=cls.min_length_descricao,
        )
        return tratamento.validar_e_limpar()


class CodigoNCUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total dos dados de um código de NC existente.

    Attributes:
        min_length_descricao (ClassVar[int]): Comprimento mínimo exigido para a descrição (5 caracteres).
        id (int): Identificador único (ID) do código de NC a ser atualizado.
        descricao (Optional[str]): Nova descrição do código de NC (opcional).
        tipo (Optional[TipoNC]): Novo tipo/categoria (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    min_length_descricao: ClassVar[int] = 5

    id: int = Field(..., description="ID do código de não conformidade")
    descricao: Optional[str] = None
    tipo: Optional[TipoNC] = None
    ativo: Optional[bool] = None

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza a descrição apenas se informada na alteração.

        Args:
            v (Optional[str]): Valor da descrição informado para atualização.

        Returns:
            Optional[str]: Descrição higienizada ou `None` caso não informada.

        Raises:
            ValueError: Se a descrição fornecida não atender ao comprimento mínimo.
        """
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="descrição do código da não conformidade",
            min_length=cls.min_length_descricao,
        )
        return tratamento.validar_e_limpar()


class CodigoNCResponse(BaseModel):
    """Schema Pydantic para formatação e serialização das respostas de código de NC.

    Attributes:
        id (int): Chave primária do código de NC.
        descricao (str): Descrição do código de NC.
        tipo (TipoNC): Categoria da não conformidade.
        ativo (bool): Status de ativação do cadastro.
        created_at (Optional[datetime]): Data e hora UTC da criação do registro.
    """

    id: int
    descricao: str
    tipo: TipoNC
    ativo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)