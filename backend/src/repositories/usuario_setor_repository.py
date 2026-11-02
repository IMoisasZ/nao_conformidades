from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.usuario_setor_model import UsuarioSetorModel

class UsuarioSetorRepository:
    @staticmethod
    def criar_usuario_setor(db: Session, dados_usuario_setor: list[dict]) -> list[UsuarioSetorModel]:
        try:
            db_usuario_setor = [UsuarioSetorModel(**item) for item in dados_usuario_setor]
            db.add_all(db_usuario_setor)
            return db_usuario_setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_usuarios_setores(db:Session, usuario_id:int, skip:int=0, limit:int=100) -> list[UsuarioSetorModel]:
        return db.query(UsuarioSetorModel).filter(UsuarioSetorModel.usuario_id == usuario_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def remover_usuario_setor(db:Session, usuario_id:int) -> int:
        try:
            return (
                db.query(UsuarioSetorModel).filter(UsuarioSetorModel.usuario_id == usuario_id).delete(synchronize_session=False)
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise e