from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.usuario_model import UsuarioModel

class UsuarioRepository:
    @staticmethod
    def criar_usuario(db:Session, dados_usuario:dict) -> UsuarioModel:
        try:
            db_usuario = UsuarioModel(**dados_usuario)
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            print(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        
    @staticmethod
    def alterar_usuario(db:Session, db_usuario: UsuarioModel, usuario_dados:dict) -> UsuarioModel:
        try:
            for key, value in usuario_dados.items():
                setattr(db_usuario, key, value)
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        
    @staticmethod
    def obter_todos_usuarios(db:Session, skip:int = 0, limit:int = 100) -> list[UsuarioModel]:
        return db.query(UsuarioModel).offset(skip).limit(limit=limit).all()
    
    @staticmethod
    def obter_usuario_pelo_id(db:Session, usuario_id:int) -> UsuarioModel:
        return db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    
    @staticmethod
    def obter_usuario_pelo_codigo(db:Session, codigo_usuario:int) -> UsuarioModel:
        return db.query(UsuarioModel).filter(UsuarioModel.codigo == codigo_usuario).first()
    
    @staticmethod
    def obter_usuario_pelo_nome(db:Session, nome_usuario:str) -> UsuarioModel:
        return db.query(UsuarioModel).filter(UsuarioModel.nome == nome_usuario).first()
    
    @staticmethod
    def obter_usuario_pelo_email(db:Session, email:str) -> UsuarioModel | None:
        return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
    
    @staticmethod
    def alterar_senha(db:Session, db_usuario:UsuarioModel, nova_senha:str) -> UsuarioModel:
        try:
            db_usuario.senha = nova_senha
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e