"""Módulo de Repositório da Entidade Código de Não Conformidade.

Este módulo contém a classe `CodigoNCRepository`, responsável pela persistência,
alteração e consulta de dados referentes à tabela `cadastro_codigo_nc` no banco de dados.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.codigo_nc_model import CodigoNCModel


class CodigoNCRepository:
    """Classe de repositório para manipulação de dados de Códigos de Não Conformidade.

    Executa operações CRUD e tratamentos de transação SQL na tabela `cadastro_codigo_nc`.
    """

    @staticmethod
    def criar_codigo_nc(db: Session, dados_codigo_nc: dict) -> CodigoNCModel:
        """Cria um novo registro de código de não conformidade no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados_codigo_nc (dict): Dicionário contendo os dados do novo código de NC.

        Returns:
            CodigoNC: Instância do modelo ORM criado e persistido.

        Raises:
            SQLAlchemyError: Se ocorrer falha durante a gravação no banco de dados.
        """
        try:
            db_codigo_nc = CodigoNC(**dados_codigo_nc)
            db.add(db_codigo_nc)
            db.commit()
            db.refresh(db_codigo_nc)
            return db_codigo_nc
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_codigo_nc(
        db: Session, db_codigo_nc: CodigoNCModel, dados_codigo_nc: dict
    ) -> CodigoNCModel:
        """Altera os dados de um código de não conformidade existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_codigo_nc (CodigoNC): Instância do modelo ORM a ser atualizada.
            dados_codigo_nc (dict): Dicionário com os novos valores para os campos.

        Returns:
            CodigoNC: Instância do modelo ORM atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer erro durante a atualização no banco de dados.
        """
        try:
            for key, value in dados_codigo_nc.items():
                setattr(db_codigo_nc, key, value)

            db.commit()
            db.refresh(db_codigo_nc)
            return db_codigo_nc
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_codigos_nc(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[CodigoNCModel]:
        """Recupera a lista paginada de todos os códigos de não conformidade cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[CodigoNC]: Lista contendo as instâncias de `CodigoNC`.
        """
        return db.query(CodigoNCModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_todos_codigos_nc_ativos(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[CodigoNCModel]:
        """Recupera a lista paginada apenas dos códigos de não conformidade ativos.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[CodigoNC]: Lista contendo as instâncias de `CodigoNC` ativos.
        """
        return (
            db.query(CodigoNCModel)
            .filter(CodigoNCModel.ativo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def obter_codigo_nc_pelo_id(
        db: Session, codigo_nc_id: int
    ) -> CodigoNCModel | None:
        """Busca um código de não conformidade pela sua chave primária (ID).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_nc_id (int): Chave primária do código de NC.

        Returns:
            CodigoNC | None: Instância do modelo ORM se encontrado, ou None.
        """
        return db.query(CodigoNCModel).filter(CodigoNCModel.id == codigo_nc_id).first()

    @staticmethod
    def obter_codigo_nc_pela_descricao(
        db: Session, descricao: str
    ) -> CodigoNCModel | None:
        """Busca um código de não conformidade através da sua descrição.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            descricao (str): Descrição do código de NC a ser pesquisado.

        Returns:
            CodigoNC | None: Instância do modelo ORM se encontrado, ou None.
        """
        return (
            db.query(CodigoNCModel)
            .filter(CodigoNCModel.descricao == descricao)
            .first()
        )

    @staticmethod
    def desativar_ativar_codigo_nc(
        db: Session, db_codigo_nc: CodigoNCModel, status: bool
    ) -> CodigoNCModel:
        """Altera o status de ativação (`ativo`) de um código de não conformidade.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_codigo_nc (CodigoNC): Instância do modelo ORM a ser ativada/desativada.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            CodigoNC: Instância do modelo ORM com o status atualizado.

        Raises:
            SQLAlchemyError: Se ocorrer erro na transação com o banco de dados.
        """
        try:
            codigo_nc = db_codigo_nc
            codigo_nc.ativo = status
            db.commit()
            db.refresh(codigo_nc)
            return codigo_nc
        except SQLAlchemyError as e:
            db.rollback()
            raise e