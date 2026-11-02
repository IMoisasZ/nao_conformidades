"""Módulo de Serviço para Gestão de Setores do Usuário."""

from sqlalchemy.orm import Session

from backend.src.models.usuario_model import UsuarioModel
from backend.src.repositories.usuario_repository import UsuarioRepository
from backend.src.repositories.usuario_setor_repository import UsuarioSetorRepository
from backend.src.schemas.usuario_setor_schema import (
    UsuarioSetorLoteRequest,
    UsuarioSetorResponse,
)


class UsuarioSetorService:
    # ------------------------------- Funções helpers -------------------------------
    @staticmethod
    def verificar_usuario_id(db: Session, usuario_id: int) -> UsuarioModel:
        """Valida se o usuário existe no banco de dados."""
        usuario = UsuarioRepository.obter_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )
        if not usuario:
            raise ValueError(f"Não existe usuário com o ID {usuario_id}")
        return usuario

    # ------------------------------- Funções do sistema -------------------------------
    @staticmethod
    def sincronizar_setores_usuario(
        db: Session, dados: UsuarioSetorLoteRequest
    ) -> list[UsuarioSetorResponse]:
        """Sincroniza em lote os setores de um usuário sob uma mesma transação SQL."""
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
        """Retorna todos os vínculos de um usuário paginados."""
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