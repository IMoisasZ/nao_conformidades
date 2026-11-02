"""Módulo de Schemas Pydantic da Entidade Cliente.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes aos clientes na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados


class ClienteCreate(BaseModel):
    """Schema Pydantic para criação de novos clientes.

    Garante as regras de sanitização do nome e valores padrão durante o cadastro.

    Attributes:
        min_length_cliente (ClassVar[int]): Comprimento mínimo exigido para o nome do cliente (3 caracteres).
        nome_cliente (str): Nome do cliente a ser cadastrado (entre 3 e 150 caracteres).
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_cliente: ClassVar[int] = 3
    nome_cliente: str = Field(..., min_length=min_length_cliente, max_length=150)
    ativo: bool = True

    @field_validator("nome_cliente")
    @classmethod
    def validar_nome_cliente(cls, v: str) -> str:
        """Valida e sanitiza a string informada para o nome do cliente.

        Args:
            v (str): Valor bruto informado para o nome do cliente.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades ou duplos).

        Raises:
            ValueError: Se o nome não atuar conforme os critérios mínimos de comprimento ou caracteres válidos.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do cliente",
            min_length=cls.min_length_cliente,
        )
        return tratamento.validar_e_limpar()


class ClienteUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total de dados de um cliente existente.

    Attributes:
        min_length_cliente (ClassVar[int]): Comprimento mínimo exigido para o nome do cliente (3 caracteres).
        id (int): Identificador único (ID) do cliente a ser atualizado.
        nome_cliente (Optional[str]): Novo nome do cliente (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    min_length_cliente: ClassVar[int] = 3
    id: int = Field(..., description="ID do cliente")
    nome_cliente: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_cliente")
    @classmethod
    def validar_nome_cliente(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome do cliente apenas quando ele é informado na atualização.

        Args:
            v (Optional[str]): Valor do nome do cliente enviado para alteração.

        Returns:
            Optional[str]: String higienizada ou `None` caso o campo não tenha sido fornecido.

        Raises:
            ValueError: Se o valor informado não atenda aos parâmetros mínimos de validação.
        """
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome do cliente",
            min_length=cls.min_length_cliente,
        )
        return tratamento.validar_e_limpar()


class ClienteResponse(BaseModel):
    """Schema Pydantic para formatação das respostas e retorno de dados do cliente.

    Attributes:
        id (int): Chave primária do cliente.
        nome_cliente (str): Nome completo do cliente.
        ativo (bool): Status de ativação da conta.
        created_at (Optional[datetime]): Data e hora UTC do cadastro.
    """

    id: int
    nome_cliente: str
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        """Configurações adicionais do Pydantic para compatibilidade ORM."""

        from_attributes = True