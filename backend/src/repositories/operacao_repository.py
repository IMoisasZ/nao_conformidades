"""Módulo de Repositório da Entidade Operação.

Este módulo contém a classe `OperacaoRepository`, responsável pela persistência,
alteração e consulta de dados referentes à tabela `operacoes` no banco de dados.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.operacao_model import OperacaoModel


class OperacaoRepository:
    """Classe de repositório para manipulação de dados das Operações fabris.

    Executa operações CRUD e tratamentos de transação SQL na tabela `operacoes`.
    """

    @staticmethod
    def criar_operacao(db: Session, dados_operacao: dict) -> OperacaoModel:
        """Cria um novo registro de operação no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados_operacao (dict): Dicionário contendo os dados da nova operação.

        Returns:
            OperacaoModel: Instância do modelo ORM criado e persistido.

        Raises:
            SQLAlchemyError: Se ocorrer falha durante a gravação no banco de dados.
        """
        try:
            db_operacao = OperacaoModel(**dados_operacao)
            db.add(db_operacao)
            db.commit()
            db.refresh(db_operacao)
            return db_operacao
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_operacao(
        db: Session, db_operacao: OperacaoModel, dados_operacao: dict
    ) -> OperacaoModel:
        """Altera os dados de uma operação existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_operacao (OperacaoModel): Instância do modelo ORM a ser atualizada.
            dados_operacao (dict): Dicionário com os novos valores para os campos.

        Returns:
            OperacaoModel: Instância do modelo ORM atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer erro durante a atualização no banco de dados.
        """
        try:
            for key, value in dados_operacao.items():
                setattr(db_operacao, key, value)

            db.commit()
            db.refresh(db_operacao)
            return db_operacao
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todas_operacoes(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[OperacaoModel]:
        """Recupera a lista paginada de todas as operações cadastradas.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[OperacaoModel]: Lista contendo as instâncias de `OperacaoModel`.
        """
        return db.query(OperacaoModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_operacao_pelo_id(
        db: Session, operacao_id: int
    ) -> OperacaoModel | None:
        """Busca uma operação pela sua chave primária (ID).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            operacao_id (int): Chave primária da operação.

        Returns:
            OperacaoModel | None: Instância do modelo ORM se encontrada, ou None.
        """
        return (
            db.query(OperacaoModel)
            .filter(OperacaoModel.id == operacao_id)
            .first()
        )

    @staticmethod
    def obter_operacao_pelo_nome(
        db: Session, nome_operacao: str
    ) -> OperacaoModel | None:
        """Busca uma operação pelo seu nome descritivo.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_operacao (str): Nome da operação a ser pesquisado.

        Returns:
            OperacaoModel | None: Instância do modelo ORM se encontrada, ou None.
        """
        return (
            db.query(OperacaoModel)
            .filter(OperacaoModel.nome_operacao == nome_operacao)
            .first()
        )

    @staticmethod
    def obter_operacoes_ativas(db: Session, skip:int=0, limit:int=100) -> list[OperacaoModel]:
        """Recupera a lista contendo apenas as operações ativas.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.

        Returns:
            list[OperacaoModel]: Lista com as instâncias das operações ativas.
        """
        return (
            db.query(OperacaoModel).offset(skip).limit(limit).filter(OperacaoModel.ativo == True).all()
        )

    @staticmethod
    def desativar_ativar_operacao(
        db: Session, db_operacao: OperacaoModel, status: bool
    ) -> OperacaoModel:
        """Altera o status de ativação (`ativo`) de uma operação.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_operacao (OperacaoModel): Instância do modelo ORM a ser ativada/desativada.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            OperacaoModel: Instância do modelo ORM com o status atualizado.

        Raises:
            SQLAlchemyError: Se ocorrer erro na transação com o banco de dados.
        """
        try:
            operacao = db_operacao
            operacao.ativo = status
            db.commit()
            db.refresh(operacao)
            return operacao
        except SQLAlchemyError as e:
            db.rollback()
            raise e