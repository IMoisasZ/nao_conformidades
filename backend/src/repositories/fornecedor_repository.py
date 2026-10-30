from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.fornecedor_model import FornecedorModel

class FornecedorRepository:
    @staticmethod
    def criar_fornecedor(db:Session, fornecedor_dados: dict) -> FornecedorModel:
        try:
            db_fornecedor = FornecedorModel(**fornecedor_dados)
            db.add(db_fornecedor)
            db.commit()
            db.refresh(db_fornecedor)
            return db_fornecedor
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def alterar_fornecedor(db:Session, db_fornecedor: FornecedorModel, fornecedor_dados:dict) -> FornecedorModel:
        try:
            for key, value in fornecedor_dados.items():
                setattr(db_fornecedor, key, value)
            db.commit()
            db.refresh(db_fornecedor)
            return db_fornecedor
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_fornecedores(db:Session, skip:int = 0, limit:int = 100) -> list[FornecedorModel]:
        return db.query(FornecedorModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_fornecedor_pelo_id(db:Session, fornecedor_id:int) -> FornecedorModel | None:
        return db.query(FornecedorModel).filter(FornecedorModel.id == fornecedor_id).first()

    @staticmethod
    def obter_fornecedor_pelo_nome(db:Session, fornecedor_nome:str) -> FornecedorModel | None:
        return db.query(FornecedorModel).filter(FornecedorModel.nome_fornecedor == fornecedor_nome).first()

    @staticmethod
    def destivar_ativar_fornecedor(db:Session, db_fornecedor:FornecedorModel, status:bool) -> FornecedorModel:
        try:
            fornecedor = db_fornecedor
            fornecedor.ativo = status
            db.commit()
            db.refresh(fornecedor)
            return fornecedor
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    