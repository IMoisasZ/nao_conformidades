"""Módulo de Serviços da Entidade Operação.

Este módulo contém a classe `OperacaoService`, responsável por implementar a lógica de negócio,
validações de duplicidade de nome, checagem de existência e orquestração entre repositório e DTOs.
"""

from sqlalchemy.orm import Session

from backend.src.models.operacao_model import OperacaoModel
from backend.src.repositories.operacao_repository import OperacaoRepository
from backend.src.schemas.operacao_schema import (
    OperacaoCreate,
    OperacaoResponse,
    OperacaoUpdate,
)


class OperacaoService:
    """Classe de serviço para gerenciamento da lógica de negócio das Operações.

    Centraliza as validações antes da persistência no banco de dados e converte
    as instâncias ORM para DTOs (`OperacaoResponse`).
    """

    # ------------------------------------ Funções Helpers ------------------------------------

    @staticmethod
    def verificar_operacao_pelo_id(db: Session, operacao_id: int) -> OperacaoModel:
        """Verifica a existência de uma operação no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados.
            operacao_id (int): Chave primária da operação.

        Returns:
            OperacaoModel: Instância ORM da operação encontrada.

        Raises:
            ValueError: Se a operação não for encontrada.
        """
        operacao = OperacaoRepository.obter_operacao_pelo_id(
            db=db, operacao_id=operacao_id
        )
        if not operacao:
            raise ValueError(f"A operação com ID {operacao_id}, não existe!")
        return operacao

    @staticmethod
    def verificar_operacao_pelo_nome(
        db: Session, nome_operacao: str
    ) -> tuple[OperacaoModel | None, str]:
        """Verifica se já existe uma operação cadastrada com o nome informado.

        Args:
            db (Session): Sessão ativa do banco de dados.
            nome_operacao (str): Nome da operação a ser consultada.

        Returns:
            tuple[OperacaoModel | None, str]: Instância ORM (ou None) e mensagem de duplicidade.
        """
        operacao = OperacaoRepository.obter_operacao_pelo_nome(
            db=db, nome_operacao=nome_operacao
        )
        if not operacao:
            return None, ""
        return operacao, f"A operação {nome_operacao}, já foi cadastrada!"

    # ------------------------------------ Funções do Sistema ------------------------------------

    @staticmethod
    def criar_operacao(
        db: Session, operacao_dados: OperacaoCreate
    ) -> OperacaoResponse:
        """Cria uma nova operação no sistema após validar duplicidade de nome.

        Args:
            db (Session): Sessão ativa do banco de dados.
            operacao_dados (OperacaoCreate): DTO contendo os dados para cadastro.

        Returns:
            OperacaoResponse: DTO da operação cadastrada.

        Raises:
            ValueError: Se já existir uma operação com o mesmo nome.
        """
        operacao, msg = OperacaoService.verificar_operacao_pelo_nome(
            db=db, nome_operacao=operacao_dados.nome_operacao
        )

        if not operacao:
            operacao_dict = operacao_dados.model_dump()
            nova_operacao = OperacaoRepository.criar_operacao(
                db=db, dados_operacao=operacao_dict
            )
            return OperacaoResponse.model_validate(nova_operacao)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_operacao(
        db: Session, operacao_id: int, dados_operacao: OperacaoUpdate
    ) -> OperacaoResponse:
        """Altera os dados de uma operação existente verificando conflitos de nome.

        Args:
            db (Session): Sessão ativa do banco de dados.
            operacao_id (int): Chave primária da operação.
            dados_operacao (OperacaoUpdate): DTO contendo os dados para atualização.

        Returns:
            OperacaoResponse: DTO da operação atualizada.

        Raises:
            ValueError: Se o ID não existir ou se o novo nome já pertencer a outro registro.
        """
        operacao = OperacaoService.verificar_operacao_pelo_id(
            db=db, operacao_id=operacao_id
        )

        operacao_dict = dados_operacao.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if (
            "nome_operacao" in operacao_dict
            and operacao_dict["nome_operacao"] != operacao.nome_operacao
        ):
            operacao_existente, msg = (
                OperacaoService.verificar_operacao_pelo_nome(
                    db=db, nome_operacao=operacao_dict["nome_operacao"]
                )
            )
            if operacao_existente:
                raise ValueError(msg)

        operacao_atualizado = OperacaoRepository.alterar_operacao(
            db=db, db_operacao=operacao, dados_operacao=operacao_dict
        )
        return OperacaoResponse.model_validate(operacao_atualizado)

    @staticmethod
    def obter_todas_operacoes(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[OperacaoResponse]:
        """Recupera a lista paginada de todas as operações cadastradas.

        Args:
            db (Session): Sessão ativa do banco de dados.
            skip (int, optional): Offset da busca. Padrão é 0.
            limit (int, optional): Limite de registros. Padrão é 100.

        Returns:
            list[OperacaoResponse]: Lista de DTOs das operações.
        """
        operacoes = OperacaoRepository.obter_todas_operacoes(
            db=db, skip=skip, limit=limit
        )
        return [
            OperacaoResponse.model_validate(operacao)
            for operacao in operacoes
            if operacao is not None
        ]

    @staticmethod
    def obter_operacao_pelo_id(
        db: Session, operacao_id: int
    ) -> OperacaoResponse:
        """Busca uma operação pelo ID e a retorna formatada como DTO.

        Args:
            db (Session): Sessão ativa do banco de dados.
            operacao_id (int): Chave primária da operação.

        Returns:
            OperacaoResponse: DTO da operação encontrada.
        """
        operacao = OperacaoService.verificar_operacao_pelo_id(
            db=db, operacao_id=operacao_id
        )
        return OperacaoResponse.model_validate(operacao)

    @staticmethod
    def obter_operacao_pelo_nome(
        db: Session, nome_operacao: str
    ) -> OperacaoResponse:
        """Busca uma operação pelo nome e a retorna formatada como DTO.

        Args:
            db (Session): Sessão ativa do banco de dados.
            nome_operacao (str): Nome da operação a ser pesquisada.

        Returns:
            OperacaoResponse: DTO da operação encontrada.

        Raises:
            ValueError: Se a operação não for encontrada.
        """
        operacao, _ = OperacaoService.verificar_operacao_pelo_nome(
            db=db, nome_operacao=nome_operacao
        )
        if operacao:
            return OperacaoResponse.model_validate(operacao)
        else:
            raise ValueError(f"Operação {nome_operacao} não foi encontrado!")

    @staticmethod
    def obter_operacoes_ativas(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[OperacaoResponse]:
        """Recupera a lista paginada contendo apenas as operações ativas.

        Args:
            db (Session): Sessão ativa do banco de dados.
            skip (int, optional): Offset da busca. Padrão é 0.
            limit (int, optional): Limite de registros. Padrão é 100.

        Returns:
            list[OperacaoResponse]: Lista de DTOs das operações ativas.
        """
        operacoes = OperacaoRepository.obter_operacoes_ativas(
            db=db, skip=skip, limit=limit
        )
        return [
            OperacaoResponse.model_validate(operacao)
            for operacao in operacoes
            if operacao is not None
        ]

    @staticmethod
    def desativar_ativar_operacao(
        db: Session, operacao_id: int, status: bool
    ) -> OperacaoResponse:
        """Altera o status de ativação de uma operação.

        Args:
            db (Session): Sessão ativa do banco de dados.
            operacao_id (int): Chave primária da operação.
            status (bool): Novo status de ativação.

        Returns:
            OperacaoResponse: DTO da operação atualizada.
        """
        operacao = OperacaoService.verificar_operacao_pelo_id(
            db=db, operacao_id=operacao_id
        )
        operacao_atualizada = OperacaoRepository.desativar_ativar_operacao(
            db=db, db_operacao=operacao, status=status
        )
        return OperacaoResponse.model_validate(operacao_atualizada)