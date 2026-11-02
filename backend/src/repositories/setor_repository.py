"""Módulo de Repositório da Entidade Setor.

Este módulo contém a classe `SetorRepository`, responsável por executar as operações de
persistência, consulta e manipulação de dados referentes aos setores diretamente no banco
de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.setor_model import SetorModel


class SetorRepository:
    """Repositório de dados para a entidade `SetorModel`.

    Isola as operações de acesso ao banco de dados (CRUD) da camada de serviço,
    gerenciando transações e tratando reversões (`rollback`) em caso de exceções do SQLAlchemy.
    """

    @staticmethod
    def criar_setor(db: Session, setor_dados: dict) -> SetorModel:
        """Persiste um novo registro de setor no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_dados (dict): Dicionário contendo os atributos do setor a ser inserido.

        Returns:
            SetorModel: Instância do setor recém-criado com os dados atualizados do banco (ex: `id`).

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a persistência, executando o `rollback`.
        """
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
    def alterar_setor(
        db: Session, db_setor: SetorModel, setor_dados: dict
    ) -> SetorModel:
        """Atualiza os campos de um registro de setor existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_setor (SetorModel): Instância do setor já carregada do banco de dados.
            setor_dados (dict): Dicionário com as chaves e novos valores a serem atualizados.

        Returns:
            SetorModel: Instância do setor atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
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
    def obter_todos_setores(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[SetorModel]:
        """Consulta e retorna uma lista paginada de setores cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[SetorModel]: Lista contendo as instâncias dos setores encontrados.
        """
        return db.query(SetorModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_setor_pelo_id(db: Session, setor_id: int) -> SetorModel | None:
        """Busca um setor específico através do seu identificador único (`id`).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_id (int): Chave primária do setor desejado.

        Returns:
            SetorModel | None: Instância do setor encontrado ou `None` caso não exista.
        """
        return db.query(SetorModel).filter(SetorModel.id == setor_id).first()

    @staticmethod
    def obter_setor_pelo_nome(db: Session, nome_setor: str) -> SetorModel | None:
        """Busca um setor específico pelo nome exato cadastrado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_setor (str): Nome do setor a ser pesquisado.

        Returns:
            SetorModel | None: Instância do setor encontrada ou `None` caso não exista.
        """
        return db.query(SetorModel).filter(SetorModel.nome_setor == nome_setor).first()

    @staticmethod
    def desativar_ativar_Setor(
        db: Session, db_setor: SetorModel, status: bool
    ) -> SetorModel:
        """Altera o status de ativação (`ativo`) de um setor específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_setor (SetorModel): Instância do setor carregada do banco de dados.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            SetorModel: Instância do setor com o status alterado.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante o salvamento, executando o `rollback`.
        """
        try:
            setor = db_setor
            setor.ativo = status
            db.commit()
            db.refresh(setor)
            return setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e