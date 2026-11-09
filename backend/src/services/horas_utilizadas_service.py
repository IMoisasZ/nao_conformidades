"""Módulo de Serviço da Entidade Horas Utilizadas.

Este módulo contém a classe `HorasUtilizadasService`, responsável por intermediar
as regras de negócio, validações e a conversão entre os schemas Pydantic e os
modelos do SQLAlchemy para a gestão de apontamentos de horas por operação na RNC.
"""

from typing import List
from sqlalchemy.orm import Session

from backend.src.models.horas_utilizadas_model import HorasUtilizadasModel
from backend.src.repositories.horas_utilizadas_repository import (
    HorasUtilizadasRepository,
)
from backend.src.schemas.horas_utilizadas_schema import (
    HorasUtilizadasCreate,
    HorasUtilizadasResponse,
    HorasUtilizadasUpdate,
)


class HorasUtilizadasService:
    """Serviço responsável por gerenciar as regras de negócio de Horas Utilizadas."""

    # -------------------------------------------------------------------------
    # Funções Helpers (Validações Internas)
    # -------------------------------------------------------------------------
    @staticmethod
    def verficar_horas_utilizadas_pelo_id(
        db: Session, id_horas_utilizadas: int
    ) -> HorasUtilizadasModel:
        """Verifica a existência de um registro de hora pelo seu ID primário.

        Args:
            db (Session): Sessão ativa do banco de dados.
            id_horas_utilizadas (int): Chave primária do registro.

        Returns:
            HorasUtilizadasModel: Instância do modelo encontrada no banco.

        Raises:
            ValueError: Se o registro não for encontrado no banco de dados.
        """
        horas_utilizadas = (
            HorasUtilizadasRepository.obter_horas_utilizadas_pelo_id(
                db=db, id_horas_utilizadas=id_horas_utilizadas
            )
        )
        if not horas_utilizadas:
            raise ValueError(
                f"Não há horas utilizadas com o ID {id_horas_utilizadas}!"
            )
        return horas_utilizadas

    @staticmethod
    def verficar_horas_utilizadas_pelo_rnc_id(
        db: Session, rnc_id: int
    ) -> List[HorasUtilizadasModel]:
        """Verifica a existência de registros de horas vinculados a uma RNC.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): Identificador da RNC associada.

        Returns:
            List[HorasUtilizadasModel]: Lista com as instâncias encontradas.

        Raises:
            ValueError: Se nenhum registro for encontrado para a RNC informada.
        """
        horas_utilizadas = (
            HorasUtilizadasRepository.obter_todas_horas_utilizadas(
                db=db, rnc_id=rnc_id
            )
        )
        if not horas_utilizadas:
            raise ValueError(f"Não há horas utilizadas para a rnc_id {rnc_id}")
        return horas_utilizadas

    # -------------------------------------------------------------------------
    # Funções do Sistema (Casos de Uso)
    # -------------------------------------------------------------------------
    @staticmethod
    def criar_horas_utilizadas(
        db: Session, dados_horas_utilizadas: List[HorasUtilizadasCreate]
    ) -> List[HorasUtilizadasResponse]:
        """Processa a criação em lote dos apontamentos de horas de uma RNC.

        Note:
            Não executa `db.commit()` interno para manter a transação atômica 
            sob controle da RNCService.

        Args:
            db (Session): Sessão ativa do banco de dados.
            dados_horas_utilizadas (List[HorasUtilizadasCreate]): Lista de DTOs.

        Returns:
            List[HorasUtilizadasResponse]: Lista de DTOs serializados de resposta.

        Raises:
            Exception: Se ocorrer qualquer erro na gravação durante a transação.
        """
        try:
            novas_horas_utilizadas = [
                item.model_dump() for item in dados_horas_utilizadas
            ]

            horas_utilizadas = (
                HorasUtilizadasRepository.criar_horas_utilizadas(
                    db=db, dados_horas_utilizadas=novas_horas_utilizadas
                )
            )

            return [
                HorasUtilizadasResponse.model_validate(horas)
                for horas in horas_utilizadas
            ]
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_horas_utilizadas(
        db: Session,
        rnc_id: int,
        id_horas_utilizadas: int,
        dados_horas_utilizadas: HorasUtilizadasUpdate,
    ) -> List[HorasUtilizadasResponse]:
        """Atualiza um registro individual de hora e retorna a lista completa da RNC.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): ID da RNC associada.
            id_horas_utilizadas (int): ID da linha de apontamento a atualizar.
            dados_horas_utilizadas (HorasUtilizadasUpdate): DTO com novos dados.

        Returns:
            List[HorasUtilizadasResponse]: Lista completa e atualizada da RNC.
        """
        horas_utilizadas = (
            HorasUtilizadasService.verficar_horas_utilizadas_pelo_id(
                db=db, id_horas_utilizadas=id_horas_utilizadas
            )
        )

        horas_utilizadas_dict = dados_horas_utilizadas.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        horas_utilizadas_atualizadas = (
            HorasUtilizadasRepository.alterar_horas_utilizadas(
                db=db,
                rnc_id=rnc_id,
                db_horas_utilizadas=horas_utilizadas,
                dados_horas_utilizadas=horas_utilizadas_dict,
            )
        )

        return [
            HorasUtilizadasResponse.model_validate(horas)
            for horas in horas_utilizadas_atualizadas
        ]

    @staticmethod
    def obter_todas_horas_utilizadas(
        db: Session, rnc_id: int
    ) -> List[HorasUtilizadasResponse]:
        """Obtém todas as horas utilizadas vinculadas a uma RNC.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): ID da RNC consultada.

        Returns:
            List[HorasUtilizadasResponse]: Lista de DTOs de resposta.
        """
        horas_utilizadas = (
            HorasUtilizadasRepository.obter_todas_horas_utilizadas(
                db=db, rnc_id=rnc_id
            )
        )
        return [
            HorasUtilizadasResponse.model_validate(horas)
            for horas in horas_utilizadas
            if horas is not None
        ]

    @staticmethod
    def obter_horas_utilizadas_pelo_id(
        db: Session, id_horas_utilizadas: int
    ) -> HorasUtilizadasResponse:
        """Obtém um registro de hora específico pelo seu ID primário.

        Args:
            db (Session): Sessão ativa do banco de dados.
            id_horas_utilizadas (int): Chave primária do registro.

        Returns:
            HorasUtilizadasResponse: DTO de resposta do registro encontrado.
        """
        horas_utilizadas = (
            HorasUtilizadasService.verficar_horas_utilizadas_pelo_id(
                db=db, id_horas_utilizadas=id_horas_utilizadas
            )
        )
        return HorasUtilizadasResponse.model_validate(horas_utilizadas)

    @staticmethod
    def remover_todas_horas_utilizadas(db: Session, rnc_id: int) -> int:
        """Remove todos os lançamentos de horas associados a uma RNC.

        Args:
            db (Session): Sessão ativa do banco de dados.
            rnc_id (int): Identificador da RNC associada.

        Returns:
            int: Quantidade total de registros removidos.
        """
        horas_utilizadas = (
            HorasUtilizadasService.verficar_horas_utilizadas_pelo_rnc_id(
                db=db, rnc_id=rnc_id
            )
        )
        horas_utilizadas_removidas = (
            HorasUtilizadasRepository.remover_todas_horas_utilizadas(
                db=db, db_horas_utilizadas=horas_utilizadas
            )
        )
        return horas_utilizadas_removidas

    @staticmethod
    def remover_horas_utilizadas_pelo_id(
        db: Session, id_horas_utilizadas: int
    ) -> int:
        """Remove um registro específico de utilização de horas pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados.
            id_horas_utilizadas (int): Chave primária do registro.

        Returns:
            int: Quantidade de registros removidos (1).
        """
        horas_utilizadas = (
            HorasUtilizadasService.verficar_horas_utilizadas_pelo_id(
                db=db, id_horas_utilizadas=id_horas_utilizadas
            )
        )
        horas_utilizadas_removidas = (
            HorasUtilizadasRepository.remover_horas_utilizadas_pelo_id(
                db=db, db_horas_utilizadas=horas_utilizadas
            )
        )
        return horas_utilizadas_removidas