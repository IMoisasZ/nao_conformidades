"""Módulo de Serviço para Gestão de Setores do Usuário.

Este módulo contém a classe `UsuarioSetorService`, responsável por implementar a lógica de negócio,
validações de existência do usuário e a sincronização atômica em lote (remocão dos antigos e inserção dos novos)
dos setores vinculados aos colaboradores.
"""

from sqlalchemy.orm import Session

from backend.src.models.usuario_model import UsuarioModel
from backend.src.repositories.usuario_repository import UsuarioRepository
from backend.src.repositories.usuario_setor_repository import UsuarioSetorRepository
from backend.src.schemas.usuario_setor_schema import (
    UsuarioSetorLoteRequest,
    UsuarioSetorResponse,
)


class UsuarioSetorService:
    """Classe de serviço para gerenciamento dos vínculos entre Usuários e Setores.

    Gerencia o ciclo de vida dos relacionamentos N:N da tabela pivô `usuarios_setores`,
    garantindo que as alterações efetuadas na interface gráfica (ex: seleções do `st.multiselect`)
    sejam gravadas atomicamente sob uma mesma transação do banco de dados.
    """

    # ------------------------------- Funções Helpers -------------------------------

    @staticmethod
    def verificar_usuario_id(db: Session, usuario_id: int) -> UsuarioModel:
        """Valida a existência de um usuário cadastrado no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário a ser verificado.

        Returns:
            UsuarioModel: Instância do modelo ORM do usuário encontrado.

        Raises:
            ValueError: Se o usuário não for encontrado no banco de dados.
        """
        usuario = UsuarioRepository.obter_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )
        if not usuario:
            raise ValueError(f"Não existe usuário com o ID {usuario_id}")
        return usuario

    # ------------------------------- Funções do Sistema -------------------------------

    @staticmethod
    def sincronizar_setores_usuario(
        db: Session, dados: UsuarioSetorLoteRequest
    ) -> list[UsuarioSetorResponse]:
        """Sincroniza em lote os setores atribuídos a um determinado usuário.

        A operação é executada sob uma transação atômica que primeiro remove todos os vínculos
        existentes do usuário e em seguida insere os novos setores informados. Em caso de falha,
        é realizado o `rollback` completo das alterações.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados (UsuarioSetorLoteRequest): DTO contendo o ID do usuário e a lista de IDs dos setores selecionados.

        Returns:
            list[UsuarioSetorResponse]: Lista contendo os DTOs dos relacionamentos atualizados.

        Raises:
            ValueError: Se o usuário não existir no banco de dados.
            Exception: Se ocorrer qualquer erro durante a transação SQL.
        """
        try:
            UsuarioSetorService.verificar_usuario_id(
                db=db, usuario_id=dados.usuario_id
            )

            UsuarioSetorRepository.remover_usuario_setor(
                db=db, usuario_id=dados.usuario_id
            )

            novos_dados = [
                {"usuario_id": dados.usuario_id, "setor_id": s_id}
                for s_id in dados.setores_ids
            ]

            if novos_dados:
                UsuarioSetorRepository.criar_usuario_setor(
                    db=db, dados_usuario_setor=novos_dados
                )

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

        # Busca e retorna a lista de vínculos atualizada do usuário
        vinculos_atualizados = (
            UsuarioSetorRepository.obter_todos_usuarios_setores(
                db=db, usuario_id=dados.usuario_id
            )
        )

        return [
            UsuarioSetorResponse.model_validate(item)
            for item in vinculos_atualizados
        ]

    @staticmethod
    def obter_todos_usuarios_setores(
        db: Session, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> list[UsuarioSetorResponse]:
        """Recupera todos os vínculos de setores de um usuário de forma paginada.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário cujos setores serão pesquisados.
            skip (int, optional): Quantidade de registros a serem ignorados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[UsuarioSetorResponse]: Lista de DTOs contendo os setores vinculados ao colaborador.

        Raises:
            ValueError: Se o usuário não for encontrado no banco de dados.
        """
        UsuarioSetorService.verificar_usuario_id(
            db=db, usuario_id=usuario_id
        )

        dados_usuario_setor = (
            UsuarioSetorRepository.obter_todos_usuarios_setores(
                db=db, usuario_id=usuario_id, skip=skip, limit=limit
            )
        )

        return [
            UsuarioSetorResponse.model_validate(item)
            for item in dados_usuario_setor
            if item is not None
        ]