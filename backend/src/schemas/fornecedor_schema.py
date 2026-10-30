from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados

class FornecedorCreate(BaseModel):
    min_length_fornecedor: ClassVar[int] = 3
    nome_fornecedor:str = Field(..., min_length=min_length_fornecedor, max_length=150)
    ativo:bool = True

    @field_validator("nome_fornecedor")
    @classmethod
    def validar_nome_fornecedor(cls, v: str) -> str:
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do fornecedor",
            min_length=cls.min_length_fornecedor
        )
        return tratamento.validar_e_limpar()

class FornecedorUpdate(BaseModel):
    id:int = Field(..., description="ID do fornecedor")
    min_length_fornecedor: ClassVar[int] = 3
    nome_fornecedor: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_fornecedor")
    @classmethod
    def validar_nome_fornecedor(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome do fornecedor",
            min_length=cls.min_length_fornecedor
        )
        return tratamento.validar_e_limpar()

class FornecedorResponse(BaseModel):
    id:int
    nome_fornecedor: str
    ativo: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True