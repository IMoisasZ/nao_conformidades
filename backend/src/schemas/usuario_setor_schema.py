"""Módulo de Schemas Pydantic para Vínculo de Usuários e Setores.

Este módulo define as estruturas de validação de dados (Schemas)
para operações de criação, atualização e resposta da associação N:N 
entre usuários e setores.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UsuarioSetorLoteRequest(BaseModel):
    """Schema para receber a seleção em lote vinda do st.multiselect.
    
    Utilizado tanto no cadastro inicial quanto na alteração/sincronização dos setores.
    
    Attributes:
        usuario_id (int): ID do usuário responsável.
        setores_ids (list[int]): Lista com os IDs dos setores selecionados no multiselect.
    """

    usuario_id: int = Field(..., description="ID do usuário responsável", gt=0)
    setores_ids: list[int] = Field(
        default_factory=list,
        description="Lista de IDs dos setores atribuídos (pode ser vazia)",
    )


class UsuarioSetorCreate(BaseModel):
    """Schema para criação individual de um vínculo único entre usuário e setor.

    Attributes:
        usuario_id (int): ID do usuário.
        setor_id (int): ID do setor.
    """

    usuario_id: int = Field(..., description="ID do usuário", gt=0)
    setor_id: int = Field(..., description="ID do setor", gt=0)


class UsuarioSetorUpdate(BaseModel):
    """Schema para atualização de um registro individual de vínculo.

    Attributes:
        id (int): Chave primária da tabela associativa.
        setor_id (int): Novo ID do setor a ser associado.
    """

    id: int = Field(..., description="ID do registro de vínculo", gt=0)
    setor_id: int = Field(..., description="ID do novo setor", gt=0)


class UsuarioSetorResponse(BaseModel):
    """Schema de resposta representando a associação populada.

    Attributes:
        id (int): ID único do registro de vínculo.
        usuario_id (int): ID do usuário.
        nome_usuario (str): Nome do usuário (resolvido via @property no ORM).
        setor_id (int): ID do setor.
        nome_setor (str): Nome do setor (resolvido via @property no ORM).
        created_at (Optional[datetime]): Data/hora UTC de criação do vínculo.
    """

    id: int = Field(..., description="ID do vínculo")
    usuario_id: int = Field(..., description="ID do usuário")
    nome_usuario: str = Field(..., description="Nome do usuário responsável")
    setor_id: int = Field(..., description="ID do setor")
    nome_setor: str = Field(..., description="Nome do setor")
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioSetoresListResponse(BaseModel):
    """Schema utilitário para retornar o resumo de setores de um usuário específico."""

    usuario_id: int = Field(..., description="ID do usuário")
    nome_usuario: str = Field(..., description="Nome do usuário responsável")
    setores: list[UsuarioSetorResponse] = Field(
        default_factory=list, description="Lista de vínculos de setores"
    )

    model_config = ConfigDict(from_attributes=True)