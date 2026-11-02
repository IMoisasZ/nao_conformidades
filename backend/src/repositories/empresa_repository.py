"""Módulo de Repositório da Entidade Empresa.

Este módulo contém a classe `EmpresaRepository`, responsável por executar as operações de
persistência, consulta e manipulação de dados referentes às empresas diretamente no banco
de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.empresa_model import EmpresaModel


class EmpresaRepository:
    """Repositório de dados para a entidade `EmpresaModel`.

    Isola as operações de acesso ao banco de dados (CRUD) da camada de serviço,
    gerenciando transações e tratando reversões (`rollback`) em caso de exceções do SQLAlchemy.
    """

    @staticmethod
    def criar_empresa(db: Session, empresa_dados: dict) -> EmpresaModel:
        """Persiste um novo registro de empresa no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_dados (dict): Dicionário contendo os atributos da empresa a ser inserida.

        Returns:
            EmpresaModel: Instância da empresa recém-criada com os dados atualizados do banco (ex: `id`).

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a persistência, executando o `rollback`.
        """
        try:
            db_empresa = EmpresaModel(**empresa_dados)
            db.add(db_empresa)
            db.commit()
            db.refresh(db_empresa)
            return db_empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_empresa(
        db: Session, db_empresa: EmpresaModel, empresa_dados: dict
    ) -> EmpresaModel:
        """Atualiza os campos de um registro de empresa existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_empresa (EmpresaModel): Instância da empresa já carregada do banco de dados.
            empresa_dados (dict): Dicionário com as chaves e novos valores a serem atualizados.

        Returns:
            EmpresaModel: Instância da empresa atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
        try:
            for key, value in empresa_dados.items():
                setattr(db_empresa, key, value)

            db.commit()
            db.refresh(db_empresa)
            return db_empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todas_empresas(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[EmpresaModel]:
        """Consulta e retorna uma lista paginada de empresas cadastradas.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[EmpresaModel]: Lista contendo as instâncias das empresas encontradas.
        """
        return db.query(EmpresaModel).offset(skip).limit(limit).all()

    @staticmethod
    def obter_empresa_pelo_id(db: Session, empresa_id: int) -> EmpresaModel | None:
        """Busca uma empresa específica através do seu identificador único (`id`).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa desejada.

        Returns:
            EmpresaModel | None: Instância da empresa encontrada ou `None` caso não exista.
        """
        return db.query(EmpresaModel).filter(EmpresaModel.id == empresa_id).first()

    @staticmethod
    def obter_empresa_pelo_cnpj(db: Session, cnpj: str) -> EmpresaModel | None:
        """Busca uma empresa específica através do seu número de CNPJ.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cnpj (str): CNPJ da empresa a ser pesquisada.

        Returns:
            EmpresaModel | None: Instância da empresa encontrada ou `None` caso não exista.
        """
        return db.query(EmpresaModel).filter(EmpresaModel.cnpj == cnpj).first()

    @staticmethod
    def desativar_ativar_empresa(
        db: Session, empresa_id: int, status: bool
    ) -> EmpresaModel:
        """Altera o status de ativação (`ativo`) de uma empresa cadastrada a partir do seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa a ter o status alterado.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            EmpresaModel: Instância da empresa com o status alterado.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a busca ou salvamento, executando o `rollback`.
        """
        try:
            empresa = (
                db.query(EmpresaModel).filter(EmpresaModel.id == empresa_id).first()
            )
            empresa.ativo = status
            db.commit()
            db.refresh(empresa)
            return empresa
        except SQLAlchemyError as e:
            db.rollback()
            raise e