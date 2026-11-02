"""Módulo de Repositório da Entidade Fornecedor.

Este módulo contém a classe `FornecedorRepository`, responsável por executar as operações de
persistência, consulta e manipulação de dados referentes aos fornecedores diretamente no banco
de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.fornecedor_model import FornecedorModel


class FornecedorRepository:
    """Repositório de dados para a entidade `FornecedorModel`.

    Isola as operações de acesso ao banco de dados (CRUD) da camada de serviço,
    gerenciando transações e tratando reversões (`rollback`) em caso de exceções do SQLAlchemy.
    """

    @staticmethod
    def criar_fornecedor(db: Session, fornecedor_dados: dict) -> FornecedorModel:
        """Persiste um novo registro de fornecedor no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_dados (dict): Dicionário contendo os atributos do fornecedor a ser inserido.

        Returns:
            FornecedorModel: Instância do fornecedor recém-criado com os dados atualizados do banco (ex: `id`).

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a persistência, executando o `rollback`.
        """
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
    def alterar_fornecedor(
        db: Session, db_fornecedor: FornecedorModel, fornecedor_dados: dict
    ) -> FornecedorModel:
        """Atualiza os campos de um registro de fornecedor existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_fornecedor (FornecedorModel): Instância do fornecedor já carregada do banco de dados.
            fornecedor_dados (dict): Dicionário com as chaves e novos valores a serem atualizados.

        Returns:
            FornecedorModel: Instância do fornecedor atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
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
    def obter_todos_fornecedores(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[FornecedorModel]:
        """Consulta e retorna uma lista paginada de fornecedores cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[FornecedorModel]: Lista contendo as instâncias dos fornecedores encontrados.
        """
        return db.query(FornecedorModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_fornecedor_pelo_id(
        db: Session, fornecedor_id: int
    ) -> FornecedorModel | None:
        """Busca um fornecedor específico através do seu identificador único (`id`).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_id (int): Chave primária do fornecedor desejado.

        Returns:
            FornecedorModel | None: Instância do fornecedor encontrado ou `None` caso não exista.
        """
        return (
            db.query(FornecedorModel)
            .filter(FornecedorModel.id == fornecedor_id)
            .first()
        )

    @staticmethod
    def obter_fornecedor_pelo_nome(
        db: Session, fornecedor_nome: str
    ) -> FornecedorModel | None:
        """Busca um fornecedor específico pelo nome exato cadastrado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_nome (str): Nome do fornecedor a ser pesquisado.

        Returns:
            FornecedorModel | None: Instância do fornecedor encontrado ou `None` caso não exista.
        """
        return (
            db.query(FornecedorModel)
            .filter(FornecedorModel.nome_fornecedor == fornecedor_nome)
            .first()
        )

    @staticmethod
    def destivar_ativar_fornecedor(
        db: Session, db_fornecedor: FornecedorModel, status: bool
    ) -> FornecedorModel:
        """Altera o status de ativação (`ativo`) de um fornecedor específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_fornecedor (FornecedorModel): Instância do fornecedor carregada do banco de dados.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            FornecedorModel: Instância do fornecedor com o status alterado.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante o salvamento, executando o `rollback`.
        """
        try:
            fornecedor = db_fornecedor
            fornecedor.ativo = status
            db.commit()
            db.refresh(fornecedor)
            return fornecedor
        except SQLAlchemyError as e:
            db.rollback()
            raise e