from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.usuario_setor_model import UsuarioSetorModel

class UsuarioSetorRepository:
    @staticmethod
    def criar_usuario_setor(db: Session, dados_usuario_setor: list[dict]) -> list[UsuarioSetorModel]:
        try:
            db_usuario_setor = [UsuarioSetorModel(**item) for item in dados_usuario_setor]
            db.add_all(db_usuario_setor)
            db.commit()
            return db_usuario_setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        