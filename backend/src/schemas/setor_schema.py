"""Módulo de Schemas Pydantic da Entidade Setor.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes aos setores na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados


class SetorCreate(BaseModel):
    """Schema Pydantic para criação de novos setores.

    Garante as regras de sanitização do nome e valores padrão durante o cadastro.

    Attributes:
        min_length_nome_setor (ClassVar[int]): Comprimento mínimo exigido para o nome do setor (3 caracteres).
        nome_setor (str): Nome do setor a ser cadastrado (entre 3 e 150 caracteres).
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_nome_setor: ClassVar[int] = 3
    nome_setor: str = Field(
        ...,
        min_length=min_length_nome_setor,
        max_length=150,
        description="Nome do setor",
    )
    ativo: bool = True

    @field_validator("nome_setor")
    @classmethod
    def validar_nome_setor(cls, v: str) -> str:
        """Valida e sanitiza a string informada para o nome do setor.

        Args:
            v (str): Valor bruto informado para o nome do setor.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades ou duplos).

        Raises:
            ValueError: Se o nome não atender aos critérios mínimos de comprimento ou formatação.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do setor",
            min_length=cls.min_length_nome_setor,
        )
        return tratamento.validar_e_limpar()


class SetorUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total dos dados de um setor existente.

    Attributes:
        min_length_nome_setor (ClassVar[int]): Comprimento mínimo exigido para o nome do setor (3 caracteres).
        id (int): Identificador único (ID) do setor a ser atualizado.
        nome_setor (Optional[str]): Novo nome do setor (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    min_length_nome_setor: ClassVar[int] = 3
    id: int = Field(..., description="ID do setor a ser atualizado")
    nome_setor: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_setor")
    @classmethod
    def validar_nome_setor(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome do setor apenas quando ele é informado na alteração.

        Args:
            v (Optional[str]): Valor do nome informado para atualização.

        Returns:
            Optional[str]: Nome higienizado ou `None` caso o campo não tenha sido fornecido.

        Raises:
            ValueError: Se o valor informado não atender aos parâmetros mínimos de validação.
        """
        if v is None:
            return None
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do setor",
            min_length=cls.min_length_nome_setor,
        )
        return tratamento.validar_e_limpar()


class SetorResponse(BaseModel):
    """Schema Pydantic para formatação e serialização das respostas de dados do setor.

    Attributes:
        id (int): Chave primária do setor.
        nome_setor (str): Nome do setor.
        ativo (bool): Status de ativação do setor.
        created_at (Optional[datetime]): Data e hora UTC do cadastro.
    """

    id: int
    nome_setor: str
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        """Configurações adicionais do Pydantic para compatibilidade ORM."""

        from_attributes = True