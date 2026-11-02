"""Módulo de Repositório da Entidade Cliente.

Este módulo contém a classe `ClienteRepository`, responsável por executar as operações de
persistência, consulta e manipulação de dados referentes aos clientes diretamente no banco
de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.cliente_model import ClienteModel


class ClienteRepository:
    """Repositório de dados para a entidade `ClienteModel`.

    Isola as operações de acesso ao banco de dados (CRUD) da camada de serviço,
    gerenciando transações e tratando reversões (`rollback`) em caso de exceções do SQLAlchemy.
    """

    @staticmethod
    def criar_cliente(db: Session, cliente_dados: dict) -> ClienteModel:
        """Persiste um novo registro de cliente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_dados (dict): Dicionário contendo os atributos do cliente a ser inserido.

        Returns:
            ClienteModel: Instância do cliente recém-criado com os dados atualizados do banco (ex: `id`).

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a persistência, executando o `rollback`.
        """
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
    def alterar_cliente(
        db: Session, db_cliente: ClienteModel, cliente_dados: dict
    ) -> ClienteModel:
        """Atualiza os campos de um registro de cliente existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_cliente (ClienteModel): Instância do cliente já carregada do banco de dados.
            cliente_dados (dict): Dicionário com as chaves e novos valores a serem atualizados.

        Returns:
            ClienteModel: Instância do cliente atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
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
    def obter_todos_clientes(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[ClienteModel]:
        """Consulta e retorna uma lista paginada de clientes cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[ClienteModel]: Lista contendo as instâncias dos clientes encontrados.
        """
        return db.query(ClienteModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_cliente_pelo_id(db: Session, cliente_id: int) -> ClienteModel | None:
        """Busca um cliente específico através do seu identificador único (`id`).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_id (int): Chave primária do cliente desejado.

        Returns:
            ClienteModel | None: Instância do cliente encontrado ou `None` caso não exista.
        """
        return db.query(ClienteModel).filter(ClienteModel.id == cliente_id).first()

    @staticmethod
    def obter_cliente_pelo_nome(
        db: Session, nome_cliente: str
    ) -> ClienteModel | None:
        """Busca um cliente específico pelo nome exato cadastrado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_cliente (str): Nome do cliente a ser pesquisado.

        Returns:
            ClienteModel | None: Instância do cliente encontrado ou `None` caso não exista.
        """
        return (
            db.query(ClienteModel)
            .filter(ClienteModel.nome_cliente == nome_cliente)
            .first()
        )

    @staticmethod
    def desativar_ativar_cliente(
        db: Session, db_cliente: ClienteModel, status: bool
    ) -> ClienteModel:
        """Altera o status de ativação (`ativo`) de um cliente específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_cliente (ClienteModel): Instância do cliente carregada do banco de dados.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            ClienteModel: Instância do cliente com o status alterado.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante o salvamento, executando o `rollback`.
        """
        try:
            cliente = db_cliente
            cliente.ativo = status
            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise e