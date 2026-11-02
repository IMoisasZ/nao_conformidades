"""Módulo de Serviços da Entidade Cliente.

Este módulo contém a classe `ClienteService`, responsável por implementar as regras de negócio,
validações de unicidade/existência e orquestrar a comunicação entre os controllers/views e a
camada de repositório da entidade Cliente.
"""

from sqlalchemy.orm import Session

from backend.src.models.cliente_model import ClienteModel
from backend.src.repositories.cliente_repository import ClienteRepository
from backend.src.schemas.cliente_schema import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate,
)


class ClienteService:
    """Classe de serviço para gerenciamento da lógica de negócio dos Clientes.

    Centraliza as validações necessárias antes da persistência ou alteração no banco de dados,
    convertendo instâncias de modelos ORM para DTOs (`ClienteResponse`).
    """

    # --------------------------------- Funções Helpers ---------------------------------
    @staticmethod
    def verificar_cliente_pelo_nome(
        db: Session, nome_cliente: str
    ) -> tuple[ClienteResponse | None, str]:
        """Verifica se já existe um cliente cadastrado com o nome informado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_cliente (str): Nome do cliente a ser consultado.

        Returns:
            tuple[ClienteResponse | None, str]: Tupla contendo o schema de resposta
                (ou `None` se não existir) e uma mensagem explicativa caso duplicado.
        """
        cliente = ClienteRepository.obter_cliente_pelo_nome(
            db=db, nome_cliente=nome_cliente
        )
        if not cliente:
            return None, ""
        return cliente, f"Já existe um cliente com o nome {nome_cliente}"

    @staticmethod
    def verificar_cliente_pelo_id(db: Session, cliente_id: int) -> ClienteModel:
        """Verifica a existência de um cliente no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_id (int): Chave primária do cliente.

        Returns:
            ClienteModel: Instância do modelo ORM do cliente encontrado.

        Raises:
            ValueError: Se o cliente não for encontrado no banco de dados.
        """
        cliente = ClienteRepository.obter_cliente_pelo_id(
            db=db, cliente_id=cliente_id
        )
        if not cliente:
            raise ValueError(
                f"Cliente com o ID {cliente_id} não encontrado ou inexistente"
            )
        return cliente

    # --------------------------------- Funções do Sistema ---------------------------------

    @staticmethod
    def criar_cliente(
        db: Session, cliente_dados: ClienteCreate
    ) -> ClienteResponse:
        """Executa a lógica de criação de um novo cliente após validar se o nome já está em uso.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_dados (ClienteCreate): DTO com os dados validados para cadastro.

        Returns:
            ClienteResponse: DTO contendo os dados do cliente cadastrado.

        Raises:
            ValueError: Se já existir um cliente cadastrado com o mesmo nome.
        """
        cliente, msg = ClienteService.verificar_cliente_pelo_nome(
            db=db, nome_cliente=cliente_dados.nome_cliente
        )
        if not cliente:
            cliente_dict = cliente_dados.model_dump()
            novo_cliente = ClienteRepository.criar_cliente(
                db=db, cliente_dados=cliente_dict
            )
            return ClienteResponse.model_validate(novo_cliente)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_cliente(
        db: Session, cliente_id: int, cliente_dados: ClienteUpdate
    ) -> ClienteResponse:
        """Altera os dados de um cliente existente verificando conflitos de duplicidade de nome.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_id (int): Chave primária do cliente a ser alterado.
            cliente_dados (ClienteUpdate): DTO contendo os novos dados para atualização.

        Returns:
            ClienteResponse: DTO contendo os dados do cliente atualizado.

        Raises:
            ValueError: Se o cliente não for encontrado ou se o novo nome já pertencer a outro cliente.
        """
        cliente = ClienteService.verificar_cliente_pelo_id(
            db=db, cliente_id=cliente_id
        )

        cliente_dict = cliente_dados.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if (
            "nome_cliente" in cliente_dict
            and cliente_dict["nome_cliente"] != cliente.nome_cliente
        ):
            cliente_existente, msg = (
                ClienteService.verificar_cliente_pelo_nome(
                    db=db, nome_cliente=cliente_dict["nome_cliente"]
                )
            )
            if cliente_existente:
                raise ValueError(msg)

        cliente_atualizado = ClienteRepository.alterar_cliente(
            db=db, db_cliente=cliente, cliente_dados=cliente_dict
        )
        return ClienteResponse.model_validate(cliente_atualizado)

    @staticmethod
    def obter_todos_clientes(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[ClienteResponse]:
        """Recupera a lista paginada de clientes e converte os registros para DTOs de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros para ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[ClienteResponse]: Lista de DTOs dos clientes cadastrados.
        """
        clientes = ClienteRepository.obter_todos_clientes(
            db=db, skip=skip, limit=limit
        )
        return [
            ClienteResponse.model_validate(cliente)
            for cliente in clientes
            if cliente is not None
        ]

    @staticmethod
    def obter_cliente_pelo_id(
        db: Session, cliente_id: int
    ) -> ClienteResponse:
        """Busca um cliente pelo seu ID e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_id (int): Chave primária do cliente.

        Returns:
            ClienteResponse: DTO com os dados do cliente encontrado.

        Raises:
            ValueError: Se o cliente não for encontrado no banco de dados.
        """
        cliente = ClienteService.verificar_cliente_pelo_id(
            db=db, cliente_id=cliente_id
        )
        return ClienteResponse.model_validate(cliente)

    @staticmethod
    def obter_cliente_pelo_nome(
        db: Session, nome_clinete: str
    ) -> ClienteResponse:
        """Busca um cliente pelo seu nome e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_clinete (str): Nome do cliente a ser pesquisado.

        Returns:
            ClienteResponse: DTO com os dados do cliente encontrado.

        Raises:
            ValueError: Se o cliente com o nome especificado não for encontrado.
        """
        cliente, _ = ClienteService.verificar_cliente_pelo_nome(
            db=db, nome_cliente=nome_clinete
        )
        if cliente:
            return ClienteResponse.model_validate(cliente)
        else:
            raise ValueError(f"Cliente {nome_clinete} não encontrado.")

    @staticmethod
    def desativar_ativar_cliente(
        db: Session, cliente_id: int, status: bool
    ) -> ClienteResponse:
        """Altera o status de ativação (`ativo`) de um cliente específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cliente_id (int): Chave primária do cliente.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            ClienteResponse: DTO com os dados do cliente atualizados.

        Raises:
            ValueError: Se o cliente não for encontrado no banco de dados.
        """
        cliente = ClienteService.verificar_cliente_pelo_id(
            db=db, cliente_id=cliente_id
        )
        cliente_atualizado = ClienteRepository.desativar_ativar_cliente(
            db=db, db_cliente=cliente, status=status
        )
        return ClienteResponse.model_validate(cliente_atualizado)