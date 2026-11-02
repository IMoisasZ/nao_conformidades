"""Módulo de Schemas Pydantic da Entidade Fornecedor.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes aos fornecedores na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados


class FornecedorCreate(BaseModel):
    """Schema Pydantic para criação de novos fornecedores.

    Garante as regras de sanitização do nome e valores padrão durante o cadastro.

    Attributes:
        min_length_fornecedor (ClassVar[int]): Comprimento mínimo exigido para o nome do fornecedor (3 caracteres).
        nome_fornecedor (str): Nome ou razão social do fornecedor (entre 3 e 150 caracteres).
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_fornecedor: ClassVar[int] = 3
    nome_fornecedor: str = Field(
        ..., min_length=min_length_fornecedor, max_length=150
    )
    ativo: bool = True

    @field_validator("nome_fornecedor")
    @classmethod
    def validar_nome_fornecedor(cls, v: str) -> str:
        """Valida e sanitiza a string informada para o nome do fornecedor.

        Args:
            v (str): Valor bruto informado para o nome do fornecedor.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades ou duplos).

        Raises:
            ValueError: Se o nome não atender aos critérios mínimos de comprimento ou caracteres válidos.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do fornecedor",
            min_length=cls.min_length_fornecedor,
        )
        return tratamento.validar_e_limpar()


class FornecedorUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total de dados de um fornecedor existente.

    Attributes:
        id (int): Identificador único (ID) do fornecedor a ser atualizado.
        min_length_fornecedor (ClassVar[int]): Comprimento mínimo exigido para o nome do fornecedor (3 caracteres).
        nome_fornecedor (Optional[str]): Novo nome do fornecedor (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    id: int = Field(..., description="ID do fornecedor")
    min_length_fornecedor: ClassVar[int] = 3
    nome_fornecedor: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_fornecedor")
    @classmethod
    def validar_nome_fornecedor(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome do fornecedor apenas quando ele é informado na atualização.

        Args:
            v (Optional[str]): Valor do nome do fornecedor enviado para alteração.

        Returns:
            Optional[str]: String higienizada ou `None` caso o campo não tenha sido fornecido.

        Raises:
            ValueError: Se o valor informado não atender aos parâmetros mínimos de validação.
        """
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome do fornecedor",
            min_length=cls.min_length_fornecedor,
        )
        return tratamento.validar_e_limpar()


class FornecedorResponse(BaseModel):
    """Schema Pydantic para formatação das respostas e retorno de dados do fornecedor.

    Attributes:
        id (int): Chave primária do fornecedor.
        nome_fornecedor (str): Nome do fornecedor.
        ativo (bool): Status de ativação da conta.
        created_at (Optional[datetime]): Data e hora UTC do cadastro.
    """

    id: int
    nome_fornecedor: str
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        """Configurações adicionais do Pydantic para compatibilidade ORM."""

        from_attributes = True