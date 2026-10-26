from datetime import datetime
from typing import Optional, ClassVar
from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.src.models.usuario_model import TipoUsuario
from backend.src.utils.tratamento_dados_util import TratamentoDados
from backend.src.utils.tratamento_qtde_caracteres_util import TratamentoNumeroCaracteres


class UsuarioCreate(BaseModel):
    min_length_nome_usuario: ClassVar[int] = 10
    num_caracteres_senha: ClassVar[int] = 5

    codigo: int = Field(..., description="Código do usuário")
    nome: str = Field(..., min_length=min_length_nome_usuario, max_length=200, description="Nome do usuário")
    email: str = Field(..., max_length=200, description="E-mail do usuário")
    tipo_usuario: TipoUsuario = Field(..., description="Tipo/Nível de permissão do usuário")
    senha: str = Field(..., description="Senha do usuário")
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def validar_nome_usuario(cls, v: str) -> str:
        tratamento = TratamentoDados(
            value=v,
            name_value="nome do usuário",
            min_length=cls.min_length_nome_usuario
        )
        return tratamento.validar_e_limpar()

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        if not v:
            raise ValueError("A senha não pode ser vazia.")
        
        tratamento = TratamentoNumeroCaracteres().qtde_caracteres(
            senha=v, 
            num_caracteres=cls.num_caracteres_senha
        )
        if not tratamento:
            raise ValueError(f"A senha deve ter exatamente {cls.num_caracteres_senha} caracteres!")
        return v


class UsuarioUpdate(BaseModel):
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
        if v is None:
            return None

        tratamento = TratamentoDados(
            value=v,
            name_value="nome do usuário",
            min_length=cls.min_length_nome_usuario
        )
        return tratamento.validar_e_limpar()


class UsuarioUpdateSenha(BaseModel):
    num_caracteres_senha: ClassVar[int] = 5

    id: int = Field(..., description="ID do usuário que terá a senha alterada")
    senha: str = Field(..., description="Nova senha a ser gravada")

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        if not v:
            raise ValueError("A senha não pode ser vazia.")

        tratamento = TratamentoNumeroCaracteres().qtde_caracteres(
            senha=v, 
            num_caracteres=cls.num_caracteres_senha
        )
        if not tratamento:
            raise ValueError(f"A senha deve ter exatamente {cls.num_caracteres_senha} caracteres!")
        return v


class UsuarioResponse(BaseModel):
    id: int
    codigo: int
    nome: str
    email: str
    tipo_usuario: TipoUsuario
    ativo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)