from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.setor_model import SetorModel

class SetorRepository:
    @staticmethod       
    def criar_setor(db: Session, setor_dados:dict) -> SetorModel:
        try:
            db_setor = SetorModel(**setor_dados)
            db.add(db_setor)
            db.commit()
            db.refresh(db_setor)
            return db_setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def alterar_setor(db:Session, db_setor: SetorModel, setor_dados:dict) -> SetorModel:
        try:
            for key, value in setor_dados.items():
                setattr(db_setor, key, value)
                
            db.commit()
            db.refresh(db_setor)
            return db_setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        
    @staticmethod
    def obter_todos_setores(db: Session, skip:int = 0, limit:int = 100) -> list[SetorModel]:
        return db.query(SetorModel).offset(skip).limit(limit).all()
    
    @staticmethod
    def obter_setor_pelo_id(db:Session, setor_id:int) -> SetorModel | None:
        return db.query(SetorModel).filter(SetorModel.id == setor_id).first()

    @staticmethod
    def obter_setor_pelo_nome(db:Session, nome_setor:str) -> SetorModel | None:
        return db.query(SetorModel).filter(SetorModel.nome_setor == nome_setor).first()
    
    @staticmethod
    def desativar_ativar_Setor(db:Session, db_setor:SetorModel, status:bool) -> SetorModel:
        try:
            setor = db_setor
            setor.ativo = status
            db.commit()
            db.refresh(setor)
            return setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e