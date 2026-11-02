"""Módulo de Serviços da Entidade Empresa.

Este módulo contém a classe `EmpresaService`, responsável por implementar as regras de negócio,
validações de unicidade de CNPJ, checagem de existência e orquestrar a comunicação entre as
views/controllers e a camada de repositório da entidade Empresa.
"""

from sqlalchemy.orm import Session

from backend.src.models.empresa_model import EmpresaModel
from backend.src.repositories.empresa_repository import EmpresaRepository
from backend.src.schemas.empresa_schema import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
)


class EmpresaService:
    """Classe de serviço para gerenciamento da lógica de negócio das Empresas.

    Centraliza as validações necessárias antes da persistência ou alteração no banco de dados,
    convertendo instâncias de modelos ORM para DTOs (`EmpresaResponse`).
    """

    # -------------------------------------------------- Funções Helpers --------------------------------------------------

    @staticmethod
    def empresa_cadastrada_cnpj(db: Session, cnpj: str) -> EmpresaModel | None:
        """Verifica se já existe uma empresa cadastrada com o CNPJ informado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cnpj (str): Número do CNPJ a ser consultado.

        Returns:
            EmpresaModel | None: Retorna a empresa caso encontrada (antes de disparar exceção) ou None.

        Raises:
            ValueError: Se já existir uma empresa cadastrada com o mesmo CNPJ.
        """
        empresa_cadastrada = EmpresaRepository.obter_empresa_pelo_cnpj(
            db=db, cnpj=cnpj
        )
        if empresa_cadastrada:
            raise ValueError("Empresa já cadastrada!")
        return empresa_cadastrada

    @staticmethod
    def empresa_cadastrada_id(db: Session, empresa_id: int) -> EmpresaModel:
        """Verifica a existência de uma empresa no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa.

        Returns:
            EmpresaModel: Instância do modelo ORM da empresa encontrada.

        Raises:
            ValueError: Se a empresa não for encontrada no banco de dados.
        """
        empresa = EmpresaRepository.obter_empresa_pelo_id(
            db=db, empresa_id=empresa_id
        )
        if not empresa:
            raise ValueError(f"Empresa com id {empresa_id} não cadastrada.")
        return empresa

    # -------------------------------------------------- Funções do Sistema --------------------------------------------------

    @staticmethod
    def criar_empresa(
        db: Session, empresa_dados: EmpresaCreate
    ) -> EmpresaResponse:
        """Executa a lógica de criação de uma nova empresa após validar a unicidade do CNPJ.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_dados (EmpresaCreate): DTO contendo os dados validados para cadastro.

        Returns:
            EmpresaResponse: DTO contendo os dados da empresa cadastrada.

        Raises:
            ValueError: Se já existir uma empresa cadastrada com o mesmo CNPJ.
        """
        EmpresaService.empresa_cadastrada_cnpj(db=db, cnpj=empresa_dados.cnpj)
        empresa_dict = empresa_dados.model_dump()
        nova_empresa = EmpresaRepository.criar_empresa(
            db=db, empresa_dados=empresa_dict
        )
        return EmpresaResponse.model_validate(nova_empresa)

    @staticmethod
    def alterar_empresa(
        db: Session, empresa_id: int, empresa_dados: EmpresaUpdate
    ) -> EmpresaResponse:
        """Altera os dados de uma empresa existente verificando conflitos de duplicidade de CNPJ.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa a ser alterada.
            empresa_dados (EmpresaUpdate): DTO contendo os novos dados para atualização.

        Returns:
            EmpresaResponse: DTO contendo os dados da empresa atualizada.

        Raises:
            ValueError: Se a empresa não for encontrada ou se o novo CNPJ já pertencer a outra empresa.
        """
        empresa = EmpresaService.empresa_cadastrada_id(
            db=db, empresa_id=empresa_id
        )
        empresa_dict = empresa_dados.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        if "cnpj" in empresa_dict and empresa_dict["cnpj"] != empresa.cnpj:
            EmpresaService.empresa_cadastrada_cnpj(
                db=db, cnpj=empresa_dict["cnpj"]
            )

        empresa_atualizada = EmpresaRepository.alterar_empresa(
            db=db, db_empresa=empresa, empresa_dados=empresa_dict
        )
        return EmpresaResponse.model_validate(empresa_atualizada)

    @staticmethod
    def obter_todas_empresas(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[EmpresaResponse]:
        """Recupera a lista paginada de empresas e converte os registros para DTOs de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros para ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[EmpresaResponse]: Lista de DTOs das empresas cadastradas.
        """
        empresas = EmpresaRepository.obter_todas_empresas(
            db=db, skip=skip, limit=limit
        )
        return [
            EmpresaResponse.model_validate(empresa)
            for empresa in empresas
            if empresa is not None
        ]

    @staticmethod
    def obter_empresa_pelo_id(
        db: Session, empresa_id: int
    ) -> EmpresaResponse:
        """Busca uma empresa pelo seu ID e a retorna formatada como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa.

        Returns:
            EmpresaResponse: DTO com os dados da empresa encontrada.

        Raises:
            ValueError: Se a empresa não for encontrada no banco de dados.
        """
        empresa = EmpresaService.empresa_cadastrada_id(
            db=db, empresa_id=empresa_id
        )
        return EmpresaResponse.model_validate(empresa)

    @staticmethod
    def obter_empresa_pelo_cnpj(
        db: Session, cnpj: str
    ) -> EmpresaResponse | None:
        """Busca uma empresa pelo número de CNPJ e a retorna formatada como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            cnpj (str): Número do CNPJ a ser pesquisado.

        Returns:
            EmpresaResponse | None: DTO com os dados da empresa encontrada ou None caso inexistente.
        """
        empresa = EmpresaRepository.obter_empresa_pelo_cnpj(db=db, cnpj=cnpj)
        if empresa:
            return EmpresaResponse.model_validate(empresa)
        return None

    @staticmethod
    def desativar_ativar_empresa(
        db: Session, empresa_id: int, status: bool
    ) -> EmpresaResponse:
        """Altera o status de ativação (`ativo`) de uma empresa específica.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            empresa_id (int): Chave primária da empresa.
            status (bool): Novo status de ativação (`True` para ativo, `False` para inativo).

        Returns:
            EmpresaResponse: DTO com os dados da empresa atualizada.

        Raises:
            ValueError: Se a empresa não for encontrada no banco de dados.
        """
        EmpresaService.empresa_cadastrada_id(db=db, empresa_id=empresa_id)
        empresa_alterada = EmpresaRepository.desativar_ativar_empresa(
            db=db, empresa_id=empresa_id, status=status
        )
        return EmpresaResponse.model_validate(empresa_alterada)