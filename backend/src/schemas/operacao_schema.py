"""Módulo de Schemas Pydantic da Entidade Operação.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes às operações fabris na aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.src.utils.tratamento_dados_util import TratamentoDados


class OperacaoCreate(BaseModel):
    """Schema Pydantic para criação de novas operações.

    Attributes:
        min_length_nome_operacao (ClassVar[int]): Comprimento mínimo exigido para o nome da operação (3 caracteres).
        nome_operacao (str): Nome descritivo da operação (entre 3 e 200 caracteres).
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_nome_operacao: ClassVar[int] = 3

    nome_operacao: str = Field(
        ...,
        min_length=min_length_nome_operacao,
        max_length=200,
        description="Nome da operação",
    )
    ativo: bool = True

    @field_validator("nome_operacao")
    @classmethod
    def validar_nome_operacao(cls, v: str) -> str:
        """Valida e sanitiza o nome da operação fornecido.

        Args:
            v (str): Valor bruto informado para o nome da operação.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades).

        Raises:
            ValueError: Se o nome não atender aos critérios mínimos de tamanho.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome da operação",
            min_length=cls.min_length_nome_operacao,
        )
        return tratamento.validar_e_limpar()


class OperacaoUpdate(BaseModel):
    """Schema Pydantic para atualização dos dados de uma operação existente.

    Attributes:
        min_length_nome_operacao (ClassVar[int]): Comprimento mínimo exigido para o nome da operação (3 caracteres).
        id (int): Identificador único (ID) da operação a ser atualizada.
        nome_operacao (Optional[str]): Novo nome da operação (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    min_length_nome_operacao: ClassVar[int] = 3

    id: int = Field(..., description="ID da operação")
    nome_operacao: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_operacao")
    @classmethod
    def validar_nome_operacao(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome da operação apenas se informado na alteração.

        Args:
            v (Optional[str]): Valor do nome da operação informado para atualização.

        Returns:
            Optional[str]: Nome higienizado ou `None` caso não informado.

        Raises:
            ValueError: Se o nome fornecido não atender ao comprimento mínimo.
        """
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome da operação",
            min_length=cls.min_length_nome_operacao,
        )
        return tratamento.validar_e_limpar()


class OperacaoResponse(BaseModel):
    """Schema Pydantic para formatação e serialização das respostas da entidade Operação.

    Attributes:
        id (int): Chave primária da operação.
        nome_operacao (str): Nome da operação.
        ativo (bool): Status de ativação do cadastro.
        created_at (Optional[datetime]): Data e hora UTC da criação do registro.
    """

    id: int
    nome_operacao: str
    ativo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)