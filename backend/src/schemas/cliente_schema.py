from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados

class ClienteCreate(BaseModel):
    min_length_cliente: ClassVar[int] = 3
    nome_cliente: str = Field(..., min_length=min_length_cliente, max_length=150)
    ativo: bool = True

    @field_validator("nome_cliente")
    @classmethod
    def validar_nome_cliente(cls, v: str) -> str:
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do cliente",
            min_length=cls.min_length_cliente
        )
        return tratamento.validar_e_limpar()

class ClienteUpdate(BaseModel):
    min_length_cliente: ClassVar[int] = 3
    id:int = Field(..., description="ID do cliente")
    nome_cliente: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_cliente")
    @classmethod
    def validar_nome_cliente(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None

        tratamento = TratamentoDados(
            value = v,
            name_value="nome do cliente",
            min_length=cls.min_length_cliente
        )
        return tratamento.validar_e_limpar()

class ClienteResponse(BaseModel):
    id: int
    nome_cliente: str
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True