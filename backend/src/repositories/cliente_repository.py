from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.src.models.cliente_model import ClienteModel

class ClienteRepository:
    @staticmethod
    def criar_cliente(db:Session, cliente_dados: dict) -> ClienteModel:
        try:
            db_cliente = ClienteModel(**cliente_dados)
            db.add(db_cliente)
            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_cliente(db:Session, db_cliente: ClienteModel, cliente_dados: dict) -> ClienteModel:
        try:
            for key, value in cliente_dados.items():
                setattr(db_cliente, key, value)

            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_clientes(db:Session, skip:int = 0, limit:int = 100) -> list[ClienteModel]:
        return db.query(ClienteModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_cliente_pelo_id(db:Session, cliente_id:int) -> ClienteModel | None:
        return db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()

    @staticmethod
    def obter_cliente_pelo_nome(db:Session, nome_cliente:str) -> ClienteModel | None:
        return db.query(ClienteModel).filter(ClienteModel.nome_cliente == nome_cliente).first()    

    @staticmethod
    def desativar_ativar_cliente(db:Session, db_cliente: ClienteModel, status:bool) -> ClienteModel:
        try:
            cliente = db_cliente
            cliente.ativo = status
            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise e
