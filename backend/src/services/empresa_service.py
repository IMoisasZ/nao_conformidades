from sqlalchemy.orm import Session
from backend.src.models.empresa_model import EmpresaModel
from backend.src.repositories.empresa_repository import EmpresaRepository
from backend.src.schemas.empresa_schema import EmpresaCreate, EmpresaUpdate, EmpresaResponse

class EmpresaService:
    # -------------------------------------------------- Funções helpers --------------------------------------------------
    @staticmethod
    def empresa_cadastrada_cnpj(db:Session, cnpj:str) -> EmpresaModel:
        empresa_cadastrada = EmpresaRepository.obter_empresa_pelo_cnpj(db=db, cnpj=cnpj)
        if empresa_cadastrada:
            raise ValueError("Empresa ja cadastrada!")
        return empresa_cadastrada

    @staticmethod
    def empresa_cadastrada_id(db:Session, empresa_id:int) -> EmpresaModel:
        empresa = EmpresaRepository.obter_empresa_pelo_id(db=db, empresa_id=empresa_id)
        if not empresa:
            raise ValueError(f"Empresa com id {empresa_id} não cadastrada.")
        return empresa

    # -------------------------------------------------- Funções do sistema --------------------------------------------------
    @staticmethod
    def criar_empresa(db: Session, empresa_dados: EmpresaCreate) -> EmpresaResponse:
        EmpresaService.empresa_cadastrada_cnpj(db=db, cnpj=empresa_dados.cnpj)
        empresa_dict = empresa_dados.model_dump()
        nova_empresa = EmpresaRepository.criar_empresa(db=db, empresa_dados=empresa_dict)
        return EmpresaResponse.model_validate(nova_empresa)

    @staticmethod
    def alterar_empresa(db: Session, empresa_id:int, empresa_dados: EmpresaUpdate):
        empresa = EmpresaService.empresa_cadastrada_id(db=db, empresa_id=empresa_id)
        empresa_dict = empresa_dados.model_dump(exclude_unset=True, exclude={"id"})

        if "cnpj" in empresa_dict and empresa_dict["cnpj"] != empresa.cnpj:
            EmpresaService.empresa_cadastrada_cnpj(db=db, cnpj=empresa_dict["cnpj"])

        empresa_atualizada = EmpresaRepository.alterar_empresa(db=db, db_empresa=empresa, empresa_dados=empresa_dict)
        return EmpresaResponse.model_validate(empresa_atualizada)

    @staticmethod
    def obter_todas_empresas(db:Session, skip:int = 0, limit:int = 100):
        empresas = EmpresaRepository.obter_todas_empresas(db=db, skip=skip, limit=limit)
        return [EmpresaResponse.model_validate(empresa) for empresa in empresas if empresa is not None]

    @staticmethod
    def obter_empresa_pelo_id(db:Session, empresa_id:int):
        empresa = EmpresaService.empresa_cadastrada_id(db=db, empresa_id=empresa_id)
        return EmpresaResponse.model_validate(empresa)
    
    @staticmethod
    def obter_empresa_pelo_cnpj(db:Session, cnpj:str):
        empresa = EmpresaRepository.obter_empresa_pelo_cnpj(db=db, cnpj=cnpj)
        if empresa:
            return EmpresaResponse.model_validate(empresa)
        return None
    
    @staticmethod
    def desativar_ativar_empresa(db:Session, empresa_id:int, status:bool):
        EmpresaService.empresa_cadastrada_id(db=db, empresa_id=empresa_id)
        empresa_alterada = EmpresaRepository.desativar_ativar_empresa(db=db, empresa_id=empresa_id, status=status)
        return EmpresaResponse.model_validate(empresa_alterada)