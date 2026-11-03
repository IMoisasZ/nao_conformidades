"""Módulo de Serviços da Entidade Código de Não Conformidade.

Este módulo contém a classe `CodigoNCService`, responsável por implementar as regras de negócio,
validações de unicidade de descrição, checagem de existência e orquestrar a comunicação entre as
views/controllers e a camada de repositório da entidade Código de Não Conformidade.
"""

from sqlalchemy.orm import Session

from backend.src.models.codigo_nc_model import CodigoNC
from backend.src.repositories.codigo_nc_repository import CodigoNCRepository
from backend.src.schemas.codigo_nc_schema import (
    CodigoNCCreate,
    CodigoNCResponse,
    CodigoNCUpdate,
)


class CodigoNCService:
    """Classe de serviço para gerenciamento da lógica de negócio dos Códigos de NC.

    Centraliza as validações necessárias antes da persistência ou alteração no banco de dados,
    convertendo instâncias de modelos ORM para DTOs (`CodigoNCResponse`).
    """

    # ---------------------------- Funções Helpers ----------------------------

    @staticmethod
    def verificar_codigo_nc_pelo_id(db: Session, codigo_nc_id: int) -> CodigoNC:
        """Verifica a existência de um código de NC no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_nc_id (int): Chave primária do código de NC.

        Returns:
            CodigoNC: Instância do modelo ORM do código de NC encontrado.

        Raises:
            ValueError: Se o código de NC não for encontrado no banco de dados.
        """
        codigo_nc = CodigoNCRepository.obter_codigo_nc_pelo_id(
            db=db, codigo_nc_id=codigo_nc_id
        )

        if codigo_nc:
            return codigo_nc
        raise ValueError(
            f"Não encontrado código de não conformidade com ID {codigo_nc_id}"
        )

    @staticmethod
    def verificar_codigo_nc_pelo_nome(
        db: Session, descricao: str
    ) -> tuple[CodigoNC | None, str]:
        """Verifica se já existe um código de NC cadastrado com a descrição informada.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            descricao (str): Descrição do código de NC a ser consultada.

        Returns:
            tuple[CodigoNC | None, str]: Tupla contendo o modelo ORM do código de NC
                (ou `None` se não existir) e uma mensagem explicativa caso esteja duplicado.
        """
        codigo_nc = CodigoNCRepository.obter_codigo_nc_pela_descricao(
            db=db, descricao=descricao
        )

        if codigo_nc:
            return codigo_nc, f"A descrição '{descricao}' já foi cadastrada!"
        return None, ""

    # ---------------------------- Funções do Sistema ----------------------------

    @staticmethod
    def criar_codigo_nc(
        db: Session, dados_codigo_nc: CodigoNCCreate
    ) -> CodigoNCResponse:
        """Executa a lógica de criação de um novo código de NC após validar a unicidade da descrição.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados_codigo_nc (CodigoNCCreate): DTO contendo os dados validados para cadastro.

        Returns:
            CodigoNCResponse: DTO contendo os dados do código de NC cadastrado.

        Raises:
            ValueError: Se já existir um código de NC cadastrado com a mesma descrição.
        """
        codigo_nc_descricao, msg = CodigoNCService.verificar_codigo_nc_pelo_nome(
            db=db, descricao=dados_codigo_nc.descricao
        )

        if codigo_nc_descricao:
            raise ValueError(msg)

        codigo_nc_dict = dados_codigo_nc.model_dump()
        novo_codigo_nc = CodigoNCRepository.criar_codigo_nc(
            db=db, dados_codigo_nc=codigo_nc_dict
        )
        return CodigoNCResponse.model_validate(novo_codigo_nc)

    @staticmethod
    def alterar_codigo_nc(
        db: Session, codigo_nc_id: int, dados_codigo_nc: CodigoNCUpdate
    ) -> CodigoNCResponse:
        """Altera os dados de um código de NC existente verificando conflitos de duplicidade de descrição.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_nc_id (int): Chave primária do código de NC a ser alterado.
            dados_codigo_nc (CodigoNCUpdate): DTO contendo os novos dados para atualização.

        Returns:
            CodigoNCResponse: DTO contendo os dados do código de NC atualizado.

        Raises:
            ValueError: Se o código de NC não for encontrado ou se a nova descrição já pertencer a outro registro.
        """
        codigo_nc = CodigoNCService.verificar_codigo_nc_pelo_id(
            db=db, codigo_nc_id=codigo_nc_id
        )
        codigo_nc_dict = dados_codigo_nc.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if (
            "descricao" in codigo_nc_dict
            and codigo_nc_dict["descricao"] != codigo_nc.descricao
        ):
            codigo_nc_existente, msg = (
                CodigoNCService.verificar_codigo_nc_pelo_nome(
                    db=db, descricao=codigo_nc_dict["descricao"]
                )
            )
            if codigo_nc_existente:
                raise ValueError(msg)

        codigo_nc_atualizado = CodigoNCRepository.alterar_codigo_nc(
            db=db, db_codigo_nc=codigo_nc, dados_codigo_nc=codigo_nc_dict
        )
        return CodigoNCResponse.model_validate(codigo_nc_atualizado)

    @staticmethod
    def obter_todos_codigos_nc(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[CodigoNCResponse]:
        """Recupera a lista paginada de todos os códigos de NC cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[CodigoNCResponse]: Lista de DTOs dos códigos de NC.
        """
        codigos_nc = CodigoNCRepository.obter_todos_codigos_nc(
            db=db, skip=skip, limit=limit
        )
        return [
            CodigoNCResponse.model_validate(codigo_nc)
            for codigo_nc in codigos_nc
            if codigo_nc is not None
        ]

    @staticmethod
    def obter_codigos_nc_ativos(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[CodigoNCResponse]:
        """Recupera a lista paginada apenas dos códigos de NC ativos.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[CodigoNCResponse]: Lista de DTOs dos códigos de NC ativos.
        """
        codigos_nc = CodigoNCRepository.obter_todos_codigos_nc_ativos(
            db=db, skip=skip, limit=limit
        )
        return [
            CodigoNCResponse.model_validate(codigo_nc)
            for codigo_nc in codigos_nc
            if codigo_nc is not None
        ]

    @staticmethod
    def obter_codigos_nc_pelo_id(
        db: Session, codigo_nc_id: int
    ) -> CodigoNCResponse:
        """Busca um código de NC pelo seu ID e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_nc_id (int): Chave primária do código de NC.

        Returns:
            CodigoNCResponse: DTO com os dados do código de NC encontrado.

        Raises:
            ValueError: Se o código de NC não for encontrado no banco de dados.
        """
        codigo_nc = CodigoNCService.verificar_codigo_nc_pelo_id(
            db=db, codigo_nc_id=codigo_nc_id
        )
        return CodigoNCResponse.model_validate(codigo_nc)

    @staticmethod
    def obter_codigo_nc_pelo_nome(
        db: Session, descricao: str
    ) -> CodigoNCResponse:
        """Busca um código de NC pela sua descrição e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            descricao (str): Descrição do código de NC a ser pesquisado.

        Returns:
            CodigoNCResponse: DTO com os dados do código de NC encontrado.

        Raises:
            ValueError: Se o código de NC com a descrição especificada não for encontrado.
        """
        codigo_nc, _ = CodigoNCService.verificar_codigo_nc_pelo_nome(
            db=db, descricao=descricao
        )
        if codigo_nc:
            return CodigoNCResponse.model_validate(codigo_nc)
        raise ValueError(
            f"Não encontrado código de não conformidade com a descrição: {descricao}"
        )

    @staticmethod
    def desativar_ativar_codigo_nc(
        db: Session, codigo_nc_id: int, status: bool
    ) -> CodigoNCResponse:
        """Altera o status de ativação (`ativo`) de um código de NC específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_nc_id (int): Chave primária do código de NC.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            CodigoNCResponse: DTO com os dados do código de NC atualizado.

        Raises:
            ValueError: Se o código de NC não for encontrado no banco de dados.
        """
        codigo_nc = CodigoNCService.verificar_codigo_nc_pelo_id(
            db=db, codigo_nc_id=codigo_nc_id
        )
        codigo_nc_atualizado = (
            CodigoNCRepository.desativar_ativar_codigo_nc(
                db=db, db_codigo_nc=codigo_nc, status=status
            )
        )
        return CodigoNCResponse.model_validate(codigo_nc_atualizado)