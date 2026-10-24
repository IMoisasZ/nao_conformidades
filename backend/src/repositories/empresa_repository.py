from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.empresa_model import EmpresaModel

class EmpresaRepository:
    @staticmethod       
    def criar_empresa(db: Session, empresa_dados:dict) -> EmpresaModel:
        try:
            db_empresa = EmpresaModel(**empresa_dados)
            db.add(db_empresa)
            db.commit()
            db.refresh(db_empresa)
            return db_empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def alterar_empresa(db:Session, db_empresa: EmpresaModel, empresa_dados:dict) -> EmpresaModel:
        try:
            for key, value in empresa_dados.items():
                setattr(db_empresa, key, value)
                
            db.commit()
            db.refresh(db_empresa)
            return db_empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        
    @staticmethod
    def obter_todas_empresas(db: Session, skip:int = 0, limit:int = 100) -> list[EmpresaModel]:
        return db.query(EmpresaModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def obter_empresa_pelo_id(db:Session, empresa_id:int) -> EmpresaModel | None:
        return db.query(EmpresaModel).filter(EmpresaModel.id == empresa_id).first()

    @staticmethod
    def obter_empresa_pelo_cnpj(db:Session, cnpj:str) -> EmpresaModel | None:
        return db.query(EmpresaModel).filter(EmpresaModel.cnpj == cnpj).first()
    
    @staticmethod
    def desativar_ativar_empresa(db:Session, empresa_id:int, status:bool) -> EmpresaModel:
        try:
            empresa = db.query(EmpresaModel).filter(EmpresaModel.id == empresa_id).first()
            empresa.ativo = status
            db.commit()
            db.refresh(empresa)
            return empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e