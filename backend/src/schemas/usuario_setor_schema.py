"""Módulo de Schemas Pydantic para Vínculo de Usuários e Setores.

Este módulo define as estruturas DTO (Data Transfer Objects) e regras de validação
de dados para operações de criação em lote, cadastro individual, atualização e
serialização do relacionamento muitos-para-muitos (N:N) entre usuários e setores.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UsuarioSetorLoteRequest(BaseModel):
    """Schema Pydantic para requisição de associação em lote vinda da interface grafica.

    Utilizado tanto no cadastro inicial quanto na alteração/sincronização dos setores
    de responsabilidade de um usuário (ex: entradas do `st.multiselect`).

    Attributes:
        usuario_id (int): Identificador único do usuário responsável (deve ser maior que zero).
        setores_ids (list[int]): Lista contendo os IDs dos setores selecionados (pode ser vazia caso
            todos os vínculos devam ser removidos).
    """

    usuario_id: int = Field(..., description="ID do usuário responsável", gt=0)
    setores_ids: list[int] = Field(
        default_factory=list,
        description="Lista de IDs dos setores atribuídos (pode ser vazia)",
    )


class UsuarioSetorCreate(BaseModel):
    """Schema Pydantic para criação individual de um vínculo único entre usuário e setor.

    Attributes:
        usuario_id (int): Identificador único do usuário (deve ser maior que zero).
        setor_id (int): Identificador único do setor (deve ser maior que zero).
    """

    usuario_id: int = Field(..., description="ID do usuário", gt=0)
    setor_id: int = Field(..., description="ID do setor", gt=0)


class UsuarioSetorUpdate(BaseModel):
    """Schema Pydantic para atualização individual de um registro de vínculo existente.

    Attributes:
        id (int): Chave primária do registro da tabela associativa (deve ser maior que zero).
        setor_id (int): Novo ID do setor a ser associado ao usuário (deve ser maior que zero).
    """

    id: int = Field(..., description="ID do registro de vínculo", gt=0)
    setor_id: int = Field(..., description="ID do novo setor", gt=0)


class UsuarioSetorResponse(BaseModel):
    """Schema Pydantic de resposta representando uma associação individual detalhada.

    Attributes:
        id (int): Identificador único do registro de vínculo na tabela pivô.
        usuario_id (int): Identificador único do usuário.
        nome_usuario (str): Nome do usuário responsável (resolvido via propriedade no ORM).
        setor_id (int): Identificador único do setor.
        nome_setor (str): Nome do setor sob responsabilidade (resolvido via propriedade no ORM).
        created_at (Optional[datetime]): Data e hora UTC do cadastro do vínculo.
    """

    id: int = Field(..., description="ID do vínculo")
    usuario_id: int = Field(..., description="ID do usuário")
    nome_usuario: str = Field(..., description="Nome do usuário responsável")
    setor_id: int = Field(..., description="ID do setor")
    nome_setor: str = Field(..., description="Nome do setor")
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioSetoresListResponse(BaseModel):
    """Schema Pydantic de resposta estruturada contendo o agrupamento dos setores de um usuário.

    Attributes:
        usuario_id (int): Identificador único do usuário responsável.
        nome_usuario (str): Nome do usuário responsável.
        setores (list[UsuarioSetorResponse]): Lista contendo os objetos de resposta de cada setor vinculado.
    """

    usuario_id: int = Field(..., description="ID do usuário")
    nome_usuario: str = Field(..., description="Nome do usuário responsável")
    setores: list[UsuarioSetorResponse] = Field(
        default_factory=list, description="Lista de vínculos de setores"
    )

    model_config = ConfigDict(from_attributes=True)