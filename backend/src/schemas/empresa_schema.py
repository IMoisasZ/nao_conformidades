"""Módulo de Schemas Pydantic da Entidade Empresa.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização e serialização dos dados referentes às empresas na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados


class EmpresaCreate(BaseModel):
    """Schema Pydantic para criação de novas empresas.

    Define as regras de validação do nome empresarial, higienização do CNPJ e valores padrão.

    Attributes:
        min_length_nome_empresa (ClassVar[int]): Comprimento mínimo exigido para o nome da empresa (3 caracteres).
        nome_empresa (str): Nome ou razão social da empresa (entre 3 e 150 caracteres).
        cnpj (str): Número do CNPJ da empresa.
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_nome_empresa: ClassVar[int] = 3
    nome_empresa: str = Field(
        ...,
        min_length=min_length_nome_empresa,
        max_length=150,
        description="Nome da empresa",
    )
    cnpj: str = Field(..., description="CNPJ da empresa")
    ativo: bool = True

    @field_validator("nome_empresa")
    @classmethod
    def validar_nome_empresa(cls, v: str) -> str:
        """Valida e sanitiza a string informada para o nome da empresa.

        Args:
            v (str): Valor bruto informado para o nome da empresa.

        Returns:
            str: String higienizada (sem espaços extras nas extremidades ou duplos).

        Raises:
            ValueError: Se o nome não atenda aos critérios de tamanho ou formatação.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome da empresa",
            min_length=cls.min_length_nome_empresa,
        )
        return tratamento.validar_e_limpar()

    @field_validator("cnpj")
    @classmethod
    def validar_e_limpar_cnpj(cls, v: str) -> str:
        """Valida e sanitiza o valor do CNPJ informado.

        Args:
            v (str): Valor bruto do CNPJ (pode conter pontuação ou apenas números).

        Returns:
            str: CNPJ higienizado e validado.

        Raises:
            ValueError: Se o CNPJ for inválido ou tiver menos de 14 caracteres.
        """
        tratamento = TratamentoDados(value=v, name_value="CNPJ", min_length=14)
        cnpj_limpo = tratamento.validar_e_limpar()
        return cnpj_limpo


class EmpresaUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total dos dados de uma empresa existente.

    Attributes:
        min_length_nome_empresa (ClassVar[int]): Comprimento mínimo exigido para o nome da empresa (3 caracteres).
        id (int): Identificador único (ID) da empresa a ser atualizada.
        nome_empresa (Optional[str]): Novo nome/razão social da empresa (opcional).
        cnpj (Optional[str]): Novo número de CNPJ da empresa (opcional).
        ativo (Optional[bool]): Novo status de ativação da empresa (opcional).
    """

    min_length_nome_empresa: ClassVar[int] = 3
    id: int = Field(..., description="ID da empresa a ser atualizada")
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_empresa")
    @classmethod
    def validar_nome_empresa(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome da empresa apenas se ele for informado na alteração.

        Args:
            v (Optional[str]): Valor do nome informado para atualização.

        Returns:
            Optional[str]: Nome higienizado ou `None` caso o campo não seja enviado.

        Raises:
            ValueError: Se o nome fornecido for inválido.
        """
        if v is None:
            return None
        tratamento = TratamentoDados(
            value=v,
            name_value="nome da empresa",
            min_length=cls.min_length_nome_empresa,
        )
        return tratamento.validar_e_limpar()

    @field_validator("cnpj")
    @classmethod
    def validar_e_limpar_cnpj(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o CNPJ apenas se ele for informado na alteração.

        Args:
            v (Optional[str]): Valor do CNPJ informado para atualização.

        Returns:
            Optional[str]: CNPJ higienizado ou `None` caso o campo não seja enviado.

        Raises:
            ValueError: Se o CNPJ fornecido for inválido.
        """
        if v is None:
            return None
        tratamento = TratamentoDados(value=v, name_value="CNPJ", min_length=14)
        return tratamento.validar_e_limpar()


class EmpresaResponse(BaseModel):
    """Schema Pydantic para formatação e serialização das respostas de dados da empresa.

    Attributes:
        id (int): Chave primária da empresa.
        nome_empresa (str): Nome ou razão social da empresa.
        cnpj (str): CNPJ cadastrado.
        ativo (bool): Status de ativação da empresa.
        created_at (Optional[datetime]): Data e hora UTC do cadastro.
    """

    id: int
    nome_empresa: str
    cnpj: str
    ativo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)