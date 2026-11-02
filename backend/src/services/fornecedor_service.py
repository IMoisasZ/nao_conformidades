"""Módulo de Serviços da Entidade Fornecedor.

Este módulo contém a classe `FornecedorService`, responsável por implementar as regras de negócio,
validações de unicidade de nome, checagem de existência e orquestrar a comunicação entre as
views/controllers e a camada de repositório da entidade Fornecedor.
"""

from sqlalchemy.orm import Session

from backend.src.models.fornecedor_model import FornecedorModel
from backend.src.repositories.fornecedor_repository import FornecedorRepository
from backend.src.schemas.fornecedor_schema import (
    FornecedorCreate,
    FornecedorResponse,
    FornecedorUpdate,
)


class FornecedorService:
    """Classe de serviço para gerenciamento da lógica de negócio dos Fornecedores.

    Centraliza as validações necessárias antes da persistência ou alteração no banco de dados,
    convertendo instâncias de modelos ORM para DTOs (`FornecedorResponse`).
    """

    # --------------------------------- Funções Helpers ---------------------------------

    @staticmethod
    def verificar_fornecedor_pelo_nome(
        db: Session, fornecedor_nome: str
    ) -> tuple[FornecedorModel | None, str]:
        """Verifica se já existe um fornecedor cadastrado com o nome informado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_nome (str): Nome do fornecedor a ser consultado.

        Returns:
            tuple[FornecedorModel | None, str]: Tupla contendo o modelo ORM do fornecedor
                (ou `None` se não existir) e uma mensagem explicativa caso esteja duplicado.
        """
        fornecedor = FornecedorRepository.obter_fornecedor_pelo_nome(
            db=db, fornecedor_nome=fornecedor_nome
        )
        if not fornecedor:
            return None, ""
        return (
            fornecedor,
            f"Já existe um fornecedor cadastrado com o nome {fornecedor_nome}",
        )

    @staticmethod
    def verificar_fornecedor_pelo_id(
        db: Session, fornecedor_id: int
    ) -> FornecedorModel:
        """Verifica a existência de um fornecedor no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_id (int): Chave primária do fornecedor.

        Returns:
            FornecedorModel: Instância do modelo ORM do fornecedor encontrado.

        Raises:
            ValueError: Se o fornecedor não for encontrado no banco de dados.
        """
        fornecedor = FornecedorRepository.obter_fornecedor_pelo_id(
            db=db, fornecedor_id=fornecedor_id
        )
        if not fornecedor:
            raise ValueError(
                f"Fornecedor com o ID {fornecedor_id} não encontrado ou inexistente"
            )
        return fornecedor

    # --------------------------------- Funções do Sistema ---------------------------------

    @staticmethod
    def criar_fornecedor(
        db: Session, fornecedor_dados: FornecedorCreate
    ) -> FornecedorResponse:
        """Executa a lógica de criação de um novo fornecedor após validar a unicidade do nome.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_dados (FornecedorCreate): DTO com os dados validados para cadastro.

        Returns:
            FornecedorResponse: DTO contendo os dados do fornecedor cadastrado.

        Raises:
            ValueError: Se já existir um fornecedor cadastrado com o mesmo nome.
        """
        fornecedor, msg = FornecedorService.verificar_fornecedor_pelo_nome(
            db=db, fornecedor_nome=fornecedor_dados.nome_fornecedor
        )
        if not fornecedor:
            fornecedor_dict = fornecedor_dados.model_dump()
            novo_fornecedor = FornecedorRepository.criar_fornecedor(
                db=db, fornecedor_dados=fornecedor_dict
            )
            return FornecedorResponse.model_validate(novo_fornecedor)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_fornecedor(
        db: Session, fornecedor_id: int, fornecedor_dados: FornecedorUpdate
    ) -> FornecedorResponse:
        """Altera os dados de um fornecedor existente verificando conflitos de duplicidade de nome.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_id (int): Chave primária do fornecedor a ser alterado.
            fornecedor_dados (FornecedorUpdate): DTO contendo os novos dados para atualização.

        Returns:
            FornecedorResponse: DTO contendo os dados do fornecedor atualizado.

        Raises:
            ValueError: Se o fornecedor não for encontrado ou se o novo nome já pertencer a outro fornecedor.
        """
        fornecedor = FornecedorService.verificar_fornecedor_pelo_id(
            db=db, fornecedor_id=fornecedor_id
        )

        fornecedor_dict = fornecedor_dados.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if (
            "nome_fornecedor" in fornecedor_dict
            and fornecedor_dict["nome_fornecedor"] != fornecedor.nome_fornecedor
        ):
            fornecedor_existente, msg = (
                FornecedorService.verificar_fornecedor_pelo_nome(
                    db=db, fornecedor_nome=fornecedor_dict["nome_fornecedor"]
                )
            )
            if fornecedor_existente:
                raise ValueError(msg)

        fornecedor_atualizado = FornecedorRepository.alterar_fornecedor(
            db=db, db_fornecedor=fornecedor, fornecedor_dados=fornecedor_dict
        )
        return FornecedorResponse.model_validate(fornecedor_atualizado)

    @staticmethod
    def obter_todos_fornecedores(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[FornecedorResponse]:
        """Recupera a lista paginada de fornecedores e converte os registros para DTOs de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros para ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[FornecedorResponse]: Lista de DTOs dos fornecedores cadastrados.
        """
        fornecedores = FornecedorRepository.obter_todos_fornecedores(
            db=db, skip=skip, limit=limit
        )
        return [
            FornecedorResponse.model_validate(fornecedor)
            for fornecedor in fornecedores
            if fornecedor is not None
        ]

    @staticmethod
    def obter_fornecedor_pelo_id(
        db: Session, fornecedor_id: int
    ) -> FornecedorResponse:
        """Busca um fornecedor pelo seu ID e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_id (int): Chave primária do fornecedor.

        Returns:
            FornecedorResponse: DTO com os dados do fornecedor encontrado.

        Raises:
            ValueError: Se o fornecedor não for encontrado no banco de dados.
        """
        fornecedor = FornecedorService.verificar_fornecedor_pelo_id(
            db=db, fornecedor_id=fornecedor_id
        )
        return FornecedorResponse.model_validate(fornecedor)

    @staticmethod
    def obter_fornecedor_pelo_nome(
        db: Session, fornecedor_nome: str
    ) -> FornecedorResponse:
        """Busca um fornecedor pelo seu nome e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_nome (str): Nome do fornecedor a ser pesquisado.

        Returns:
            FornecedorResponse: DTO com os dados do fornecedor encontrado.

        Raises:
            ValueError: Se o fornecedor com o nome especificado não for encontrado.
        """
        fornecedor, msg = FornecedorService.verificar_fornecedor_pelo_nome(
            db=db, fornecedor_nome=fornecedor_nome
        )
        if fornecedor:
            return FornecedorResponse.model_validate(fornecedor)
        else:
            raise ValueError(msg)

    @staticmethod
    def desativar_ativar_fornecedor(
        db: Session, fornecedor_id: int, status: bool
    ) -> FornecedorResponse:
        """Altera o status de ativação (`ativo`) de um fornecedor específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            fornecedor_id (int): Chave primária do fornecedor.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            FornecedorResponse: DTO com os dados do fornecedor atualizado.

        Raises:
            ValueError: Se o fornecedor não for encontrado no banco de dados.
        """
        fornecedor = FornecedorService.verificar_fornecedor_pelo_id(
            db=db, fornecedor_id=fornecedor_id
        )
        fornecedor_atualizado = FornecedorRepository.destivar_ativar_fornecedor(
            db=db, db_fornecedor=fornecedor, status=status
        )
        return FornecedorResponse.model_validate(fornecedor_atualizado)