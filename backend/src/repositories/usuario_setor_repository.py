"""Módulo de Repositório da Entidade de Vínculo Usuário-Setor.

Este módulo contém a classe `UsuarioSetorRepository`, responsável por executar as operações de
persistência em lote, consulta e remoção de vínculos entre usuários e setores diretamente no banco
de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.usuario_setor_model import UsuarioSetorModel


class UsuarioSetorRepository:
    """Repositório de dados para a entidade pivô `UsuarioSetorModel`.

    Isola as operações de manipulação da tabela pivô `usuarios_setores` da camada de serviço,
    gerenciando inserções/exclusões em lote e tratando reversões (`rollback`) em caso de exceções.
    """

    @staticmethod
    def criar_usuario_setor(
        db: Session, dados_usuario_setor: list[dict]
    ) -> list[UsuarioSetorModel]:
        """Insere múltiplos registros de vínculos entre usuário e setores em lote.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados_usuario_setor (list[dict]): Lista de dicionários, onde cada item
                deve conter as chaves `usuario_id` e `setor_id`.

        Returns:
            list[UsuarioSetorModel]: Lista das instâncias dos vínculos criadas.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
        try:
            db_usuario_setor = [
                UsuarioSetorModel(**item) for item in dados_usuario_setor
            ]
            db.add_all(db_usuario_setor)
            return db_usuario_setor
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_usuarios_setores(
        db: Session, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> list[UsuarioSetorModel]:
        """Consulta e retorna todos os setores vinculados a um usuário específico de forma paginada.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário para o qual os setores serão buscados.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[UsuarioSetorModel]: Lista contendo as instâncias de relacionamentos encontradas.
        """
        return (
            db.query(UsuarioSetorModel)
            .filter(UsuarioSetorModel.usuario_id == usuario_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def remover_usuario_setor(db: Session, usuario_id: int) -> int:
        """Remove todos os vínculos de setores pertencentes a um determinado usuário.

        Normalmente utilizado antes de re-inserir novos relacionamentos em lote durante a sincronização.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário cujos vínculos serão deletados.

        Returns:
            int: Quantidade total de registros deletados na operação.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a exclusão, executando o `rollback`.
        """
        try:
            return (
                db.query(UsuarioSetorModel)
                .filter(UsuarioSetorModel.usuario_id == usuario_id)
                .delete(synchronize_session=False)
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise e