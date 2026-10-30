from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from backend.src.utils.tratamento_dados_util import TratamentoDados

class SetorCreate(BaseModel):
    min_length_nome_setor: ClassVar[int] = 3
    nome_setor: str = Field(..., min_length=min_length_nome_setor, max_length=150, description="Nome do setor")
    ativo: bool = True

    @field_validator("nome_setor")
    @classmethod
    def validar_nome_setor(cls, v: str) -> str:
        tratamento = TratamentoDados(
            value=v, 
            name_value="nome do setor", 
            min_length=cls.min_length_nome_setor
        )
        return tratamento.validar_e_limpar()        

class SetorUpdate(BaseModel):
    min_length_nome_setor: ClassVar[int] = 3
    id: int = Field(..., description="ID do setor a ser atualizado")
    nome_setor: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_setor")
    @classmethod
    def validar_nome_setor(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        tratamento = TratamentoDados(
            value=v, 
            name_value="nome do setor", 
            min_length=cls.min_length_nome_setor
        )
        return tratamento.validar_e_limpar()

class SetorResponse(BaseModel):
    id: int
    nome_setor: str
    ativo: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True