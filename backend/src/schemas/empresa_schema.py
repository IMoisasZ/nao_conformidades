# src/backend/schemas/empresa_schema.py
from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.src.utils.tratamento_dados_util import TratamentoDados

class EmpresaCreate(BaseModel):
    min_length_nome_empresa: ClassVar[int] = 3
    nome_empresa: str = Field(..., min_length=min_length_nome_empresa, max_length=150, description="Nome da empresa")
    cnpj: str = Field(..., description="CNPJ da empresa")
    ativo: bool = True

    @field_validator("nome_empresa")
    @classmethod
    def validar_nome_empresa(cls, v: str) -> str:
        tratamento = TratamentoDados(
            value=v, 
            name_value="nome da empresa", 
            min_length=cls.min_length_nome_empresa
        )
        return tratamento.validar_e_limpar()
    
    @field_validator("cnpj")
    @classmethod
    def validar_e_limpar_cnpj(cls, v: str) -> str:
        tratamento = TratamentoDados(value=v, name_value="CNPJ", min_length=14)
        cnpj_limpo = tratamento.validar_e_limpar()

        return cnpj_limpo
        

class EmpresaUpdate(BaseModel):
    min_length_nome_empresa: ClassVar[int] = 3
    id: int = Field(..., description="ID da empresa a ser atualizada")
    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator("nome_empresa")
    @classmethod
    def validar_nome_empresa(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        tratamento = TratamentoDados(
            value=v, 
            name_value="nome da empresa", 
            min_length=cls.min_length_nome_empresa
        )
        return tratamento.validar_e_limpar()
    
    @field_validator("cnpj")
    @classmethod
    def validar_e_limpar_cnpj(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        tratamento = TratamentoDados(value=v, name_value="CNPJ", min_length=14)
        return tratamento.validar_e_limpar()

class EmpresaResponse(BaseModel):
    id: int
    nome_empresa: str
    cnpj: str
    ativo: bool
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)