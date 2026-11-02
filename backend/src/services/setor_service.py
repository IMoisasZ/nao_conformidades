"""Módulo de Serviços da Entidade Setor.

Este módulo contém a classe `SetorService`, responsável por implementar as regras de negócio,
validações de unicidade de nome, checagem de existência e orquestrar a comunicação entre as
views/controllers e a camada de repositório da entidade Setor.
"""

from sqlalchemy.orm import Session

from backend.src.models.setor_model import SetorModel
from backend.src.repositories.setor_repository import SetorRepository
from backend.src.schemas.setor_schema import (
    SetorCreate,
    SetorResponse,
    SetorUpdate,
)


class SetorService:
    """Classe de serviço para gerenciamento da lógica de negócio dos Setores.

    Centraliza as validações necessárias antes da persistência ou alteração no banco de dados,
    convertendo instâncias de modelos ORM para DTOs (`SetorResponse`).
    """

    # --------------------------- Funções Helpers ---------------------------

    @staticmethod
    def verifica_setor_pelo_nome(
        db: Session, nome_setor: str
    ) -> tuple[SetorModel | None, str]:
        """Verifica se já existe um setor cadastrado com o nome informado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_setor (str): Nome do setor a ser consultado.

        Returns:
            tuple[SetorModel | None, str]: Tupla contendo o modelo ORM do setor
                (ou `None` se não existir) e uma mensagem explicativa caso esteja duplicado.
        """
        setor = SetorRepository.obter_setor_pelo_nome(
            db=db, nome_setor=nome_setor
        )
        if not setor:
            return None, ""
        return setor, f"O setor {nome_setor} já foi cadastrado!"

    @staticmethod
    def verifica_setor_pelo_id(db: Session, setor_id: int) -> SetorModel:
        """Verifica a existência de um setor no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_id (int): Chave primária do setor.

        Returns:
            SetorModel: Instância do modelo ORM do setor encontrado.

        Raises:
            ValueError: Se o setor não for encontrado no banco de dados.
        """
        setor = SetorRepository.obter_setor_pelo_id(db=db, setor_id=setor_id)
        if not setor:
            raise ValueError(
                f"O ID {setor_id} não foi encontrado ou inexistente!"
            )
        return setor

    # --------------------------- Funções do Sistema ---------------------------

    @staticmethod
    def criar_setor(db: Session, setor_dados: SetorCreate) -> SetorResponse:
        """Executa a lógica de criação de um novo setor após validar a unicidade do nome.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_dados (SetorCreate): DTO com os dados validados para cadastro.

        Returns:
            SetorResponse: DTO contendo os dados do setor cadastrado.

        Raises:
            ValueError: Se já existir um setor cadastrado com o mesmo nome.
        """
        setor, msg = SetorService.verifica_setor_pelo_nome(
            db=db, nome_setor=setor_dados.nome_setor
        )

        if not setor:
            setor_dict = setor_dados.model_dump()
            novo_setor = SetorRepository.criar_setor(
                db=db, setor_dados=setor_dict
            )
            return SetorResponse.model_validate(novo_setor)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_setor(
        db: Session, setor_id: int, setor_dados: SetorUpdate
    ) -> SetorResponse:
        """Altera os dados de um setor existente verificando conflitos de duplicidade de nome.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_id (int): Chave primária do setor a ser alterado.
            setor_dados (SetorUpdate): DTO contendo os novos dados para atualização.

        Returns:
            SetorResponse: DTO contendo os dados do setor atualizado.

        Raises:
            ValueError: Se o setor não for encontrado ou se o novo nome já pertencer a outro setor.
        """
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)

        setor_dict = setor_dados.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if (
            "nome_setor" in setor_dict
            and setor_dict["nome_setor"] != setor.nome_setor
        ):
            setor_existente, msg = SetorService.verifica_setor_pelo_nome(
                db=db, nome_setor=setor_dict["nome_setor"]
            )
            if setor_existente:
                raise ValueError(msg)

        setor_atualizado = SetorRepository.alterar_setor(
            db=db, db_setor=setor, setor_dados=setor_dict
        )
        return SetorResponse.model_validate(setor_atualizado)

    @staticmethod
    def obter_todos_setores(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[SetorResponse]:
        """Recupera a lista paginada de setores e converte os registros para DTOs de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros para ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[SetorResponse]: Lista de DTOs dos setores cadastrados.
        """
        setores = SetorRepository.obter_todos_setores(
            db=db, skip=skip, limit=limit
        )
        return [
            SetorResponse.model_validate(setor)
            for setor in setores
            if setor is not None
        ]

    @staticmethod
    def obter_setor_pelo_id(db: Session, setor_id: int) -> SetorResponse:
        """Busca um setor pelo seu ID e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_id (int): Chave primária do setor.

        Returns:
            SetorResponse: DTO com os dados do setor encontrado.

        Raises:
            ValueError: Se o setor não for encontrado no banco de dados.
        """
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)
        return SetorResponse.model_validate(setor)

    @staticmethod
    def obter_setor_pelo_nome(db: Session, nome_setor: str) -> SetorResponse:
        """Busca um setor pelo seu nome e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_setor (str): Nome do setor a ser pesquisado.

        Returns:
            SetorResponse: DTO com os dados do setor encontrado.

        Raises:
            ValueError: Se o setor com o nome especificado não for encontrado.
        """
        setor, _ = SetorService.verifica_setor_pelo_nome(
            db=db, nome_setor=nome_setor
        )
        if setor:
            return SetorResponse.model_validate(setor)
        else:
            raise ValueError(f"Setor {nome_setor} não foi encontrado.")

    @staticmethod
    def desativar_ativar_setor(
        db: Session, setor_id: int, status: bool
    ) -> SetorResponse:
        """Altera o status de ativação (`ativo`) de um setor específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            setor_id (int): Chave primária do setor.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            SetorResponse: DTO com os dados do setor atualizado.

        Raises:
            ValueError: Se o setor não for encontrado no banco de dados.
        """
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)
        setor_atualizado = SetorRepository.desativar_ativar_Setor(
            db=db, db_setor=setor, status=status
        )
        return SetorResponse.model_validate(setor_atualizado)