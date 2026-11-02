"""Módulo de Schemas Pydantic da Entidade Usuário.

Este módulo define as classes DTO (Data Transfer Objects) utilizadas para validação,
higienização, atualização, alteração de senha e serialização dos dados referentes aos
usuários na API/aplicação.
"""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.src.models.usuario_model import TipoUsuario
from backend.src.utils.tratamento_dados_util import TratamentoDados
from backend.src.utils.tratamento_qtde_caracteres_util import (
    TratamentoNumeroCaracteres,
)


class UsuarioCreate(BaseModel):
    """Schema Pydantic para criação de novos usuários.

    Define regras estritas de validação para o nome do usuário (mínimo de 10 caracteres),
    sanitização do texto, validação de tamanho fixo para a senha (5 caracteres) e valores padrão.

    Attributes:
        min_length_nome_usuario (ClassVar[int]): Comprimento mínimo exigido para o nome do usuário (10 caracteres).
        num_caracteres_senha (ClassVar[int]): Quantidade exata de caracteres exigidos para a senha (5 caracteres).
        codigo (Optional[int]): Código/matrícula numérico do usuário (opcional para atribuição sequencial).
        nome (str): Nome completo do usuário (entre 10 e 200 caracteres).
        email (str): Endereço de e-mail do usuário (máximo de 200 caracteres).
        tipo_usuario (TipoUsuario): Nível de permissão/acesso do usuário (Enum `TipoUsuario`).
        senha (str): Senha de acesso com exatamente 5 caracteres.
        ativo (bool): Status inicial de ativação do cadastro (Padrão: True).
    """

    min_length_nome_usuario: ClassVar[int] = 10
    num_caracteres_senha: ClassVar[int] = 5

    codigo: Optional[int] = Field(None, description="Código do usuário")
    nome: str = Field(
        ...,
        min_length=min_length_nome_usuario,
        max_length=200,
        description="Nome do usuário",
    )
    email: str = Field(..., max_length=200, description="E-mail do usuário")
    tipo_usuario: TipoUsuario = Field(
        ..., description="Tipo/Nível de permissão do usuário"
    )
    senha: str = Field(..., description="Senha do usuário")
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def validar_nome_usuario(cls, v: str) -> str:
        """Valida e sanitiza o nome completo informado para o usuário.

        Args:
            v (str): Valor bruto do nome do usuário.

        Returns:
            str: String higienizada (sem espaços extras).

        Raises:
            ValueError: Se o nome for menor que o limite mínimo de 10 caracteres ou inválido.
        """
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do usuário",
            min_length=cls.min_length_nome_usuario,
        )
        return tratamento.validar_e_limpar()

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        """Valida se a senha atende ao critério de não ser vazia e possuir exatamente 5 caracteres.

        Args:
            v (str): Senha fornecida para o novo usuário.

        Returns:
            str: A senha validada.

        Raises:
            ValueError: Se a senha for vazia ou não contiver exatamente 5 caracteres.
        """
        senha_limpa = (v or "").strip()
        if not senha_limpa:
            raise ValueError("A senha não pode ser vazia.")

        tratamento = TratamentoNumeroCaracteres().qtde_caracteres(
            senha=v, num_caracteres=cls.num_caracteres_senha
        )
        if not tratamento:
            raise ValueError(
                f"A senha deve ter exatamente {cls.num_caracteres_senha} caracteres!"
            )
        return v


class UsuarioUpdate(BaseModel):
    """Schema Pydantic para atualização parcial ou total dos dados cadastrais do usuário.

    Attributes:
        min_length_nome_usuario (ClassVar[int]): Comprimento mínimo exigido para o nome do usuário (10 caracteres).
        id (int): Identificador único (ID) do usuário a ser atualizado.
        codigo (Optional[int]): Novo código/matrícula do usuário (opcional).
        nome (Optional[str]): Novo nome do usuário (opcional).
        email (Optional[str]): Novo e-mail do usuário (opcional).
        tipo_usuario (Optional[TipoUsuario]): Novo tipo de permissão (opcional).
        ativo (Optional[bool]): Novo status de ativação (opcional).
    """

    min_length_nome_usuario: ClassVar[int] = 10

    id: int = Field(..., description="ID do usuário a ser atualizado")
    codigo: Optional[int] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    tipo_usuario: Optional[TipoUsuario] = None
    ativo: Optional[bool] = None

    @field_validator("nome")
    @classmethod
    def validar_nome_usuario(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o nome do usuário apenas quando ele for informado na alteração.

        Args:
            v (Optional[str]): Nome do usuário enviado para atualização.

        Returns:
            Optional[str]: Nome higienizado ou `None` caso o campo não seja fornecido.

        Raises:
            ValueError: Se o nome fornecido não atender aos critérios de comprimento mínimo.
        """
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome do usuário",
            min_length=cls.min_length_nome_usuario,
        )
        return tratamento.validar_e_limpar()


class UsuarioUpdateSenha(BaseModel):
    """Schema Pydantic exclusivo para operações de redefinição/alteração de senha do usuário.

    Attributes:
        num_caracteres_senha (ClassVar[int]): Quantidade exata de caracteres exigidos para a senha (5 caracteres).
        id (int): Identificador único (ID) do usuário que terá a senha alterada.
        senha (str): Nova senha a ser gravada.
    """

    num_caracteres_senha: ClassVar[int] = 5

    id: int = Field(..., description="ID do usuário que terá a senha alterada")
    senha: str = Field(..., description="Nova senha a ser gravada")

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        """Valida se a nova senha atende ao critério de não ser vazia e ter exatamente 5 caracteres.

        Args:
            v (str): Nova senha fornecida.

        Returns:
            str: A nova senha validada.

        Raises:
            ValueError: Se a senha for vazia ou não possuir exatamente 5 caracteres.
        """
        senha_limpa = (v or "").strip()
        if not senha_limpa:
            raise ValueError("A senha não pode ser vazia.")

        tratamento = TratamentoNumeroCaracteres().qtde_caracteres(
            senha=v, num_caracteres=cls.num_caracteres_senha
        )
        if not tratamento:
            raise ValueError(
                f"A senha deve ter exatamente {cls.num_caracteres_senha} caracteres!"
            )
        return v


class UsuarioResponse(BaseModel):
    """Schema Pydantic para formatação e serialização das respostas de dados do usuário.

    Attributes:
        id (int): Chave primária do usuário.
        codigo (Optional[int]): Código/matrícula do colaborador.
        nome (str): Nome do usuário.
        email (str): Endereço de e-mail cadastrado.
        tipo_usuario (TipoUsuario): Perfil/nível de permissão do usuário.
        ativo (bool): Status de ativação da conta.
        created_at (Optional[datetime]): Data e hora UTC do cadastro.
    """

    id: int
    codigo: Optional[int] = None
    nome: str
    email: str
    tipo_usuario: TipoUsuario
    ativo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)