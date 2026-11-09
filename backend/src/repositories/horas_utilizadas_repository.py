"""Módulo de Repositório da Entidade Horas Utilizadas.

Este módulo contém a classe `HorasUtilizadasRepository`, responsável pelas operações
de acesso ao banco de dados (CRUD) para os apontamentos de horas por operação na RNC.
"""

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.horas_utilizadas_model import HorasUtilizadasModel


class HorasUtilizadasRepository:
    """Repositório de dados para a entidade HorasUtilizadas."""

    @staticmethod
    def criar_horas_utilizadas(
        db: Session, dados_horas_utilizadas: List[dict]
    ) -> List[HorasUtilizadasModel]:
        """Insere múltiplos registros de horas associados a uma RNC na sessão ativa.

        Note:
            Adiciona os objetos à sessão (`db.add_all`), mas NÃO executa o commit
            para permitir que o Service da RNC orquestre a criação atômica.

        Args:
            db (Session): Sessão ativa do banco de dados.
            dados_horas_utilizadas (List[dict]): Lista de dicionários contendo os dados.

        Returns:
            List[HorasUtilizadasModel]: Lista de modelos adicionados à sessão.
        """
        try:
            db_horas_utilizadas = [
                HorasUtilizadasModel(**item) for item in dados_horas_utilizadas
            ]
            db.add_all(db_horas_utilizadas)
            return db_horas_utilizadas
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_horas_utilizadas(
        db: Session,
        rnc_id: int,
        db_horas_utilizadas: HorasUtilizadasModel,
        dados_horas_utilizadas: dict,
    ) -> List[HorasUtilizadasModel]:
        """Atualiza um registro individual e retorna a lista completa de horas da RNC.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): ID da RNC associada.
            db_horas_utilizadas (HorasUtilizadasModel): Instância persistida a ser atualizada.
            dados_horas_utilizadas (dict): Dicionário com os novos valores.

        Returns:
            List[HorasUtilizadasModel]: Lista completa e atualizada de apontamentos da RNC.
        """
        try:
            for key, value in dados_horas_utilizadas.items():
                if value is not None and hasattr(db_horas_utilizadas, key):
                    setattr(db_horas_utilizadas, key, value)

            db.commit()
            db.refresh(db_horas_utilizadas)
            return HorasUtilizadasRepository.obter_todas_horas_utilizadas(
                db=db, rnc_id=rnc_id
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todas_horas_utilizadas(
        db: Session, rnc_id: int, skip: int = 0, limit: int = 100
    ) -> List[HorasUtilizadasModel]:
        """Obtém a lista de horas utilizadas vinculadas a uma RNC com paginação.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): Identificador da RNC associada.
            skip (int): Quantidade de registros a ignorar.
            limit (int): Limite máximo de registros retornados.

        Returns:
            List[HorasUtilizadasModel]: Lista com os lançamentos encontrados.
        """
        return (
            db.query(HorasUtilizadasModel)
            .filter(HorasUtilizadasModel.rnc_id == rnc_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def obter_horas_utilizadas_pelo_id(
        db: Session, id_horas_utilizadas: int
    ) -> Optional[HorasUtilizadasModel]:
        """Busca um registro específico de utilização de horas pelo seu ID primário.

        Args:
            db (Session): Sessão ativa do banco de dados.
            id_horas_utilizadas (int): Chave primária do registro.

        Returns:
            Optional[HorasUtilizadasModel]: Instância encontrada ou None.
        """
        return (
            db.query(HorasUtilizadasModel)
            .filter(HorasUtilizadasModel.id == id_horas_utilizadas)
            .first()
        )

    @staticmethod
    def remover_todas_horas_utilizadas(db: Session, db_horas_utilizadas: list[HorasUtilizadasModel]) -> int:
        """Remove da sessão e confirma a exclusão de uma lista de instâncias de horas.

        Args:
            db (Session): Sessão ativa do banco de dados.
            db_horas_utilizadas (List[HorasUtilizadasModel]): Lista de objetos a remover.

        Returns:
            int: Quantidade total de registros removidos.
        """
        try:
            total = len(db_horas_utilizadas)
            for item in db_horas_utilizadas:
                db.delete(item)
            db.commit()
            return total
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def remover_horas_utilizadas_pelo_id(
        db: Session, db_horas_utilizadas: HorasUtilizadasModel
    ) -> int:
        """Remove da sessão e confirma a exclusão de uma única instância de hora.

        Args:
            db (Session): Sessão ativa do banco de dados.
            db_horas_utilizadas (HorasUtilizadasModel): Objeto a ser removido.

        Returns:
            int: Quantidade de registros removidos (1).
        """
        try:
            db.delete(db_horas_utilizadas)
            db.commit()
            return 1
        except SQLAlchemyError as e:
            db.rollback()
            raise e