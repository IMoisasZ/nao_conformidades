"""Módulo de Serviços da Entidade Usuário.

Este módulo contém a classe `UsuarioService`, responsável por implementar as regras de negócio,
geração sequencial automática de códigos de colaboradores, validação de unicidade de e-mail/código,
alteração de senhas e orquestração entre as views/controllers e a camada de repositório da entidade Usuário.
"""

import os
from sqlalchemy.orm import Session

from backend.src.models.usuario_model import UsuarioModel
from backend.src.repositories.usuario_repository import UsuarioRepository
from backend.src.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    UsuarioUpdateSenha,
)


class UsuarioService:
    """Classe de serviço para gerenciamento da lógica de negócio dos Usuários.

    Centraliza a lógica de validação de duplicidade, atribuição automática de códigos sequenciais
    com base em variáveis de ambiente e conversão de modelos ORM para DTOs (`UsuarioResponse`).
    """

    # ------------------------------- Funções Helpers -------------------------------

    @staticmethod
    def verificar_usuario_pelo_email(
        db: Session, email: str, usuario_id_atual: int | None = None
    ) -> bool:
        """Verifica se o e-mail fornecido é válido e se já não está associado a outro usuário.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            email (str): Endereço de e-mail a ser verificado.
            usuario_id_atual (int | None, optional): ID do usuário atual para ignorar no caso de atualização.

        Returns:
            bool: Retorna `True` caso o e-mail esteja livre para uso.

        Raises:
            ValueError: Se o e-mail não for informado ou se já pertencer a outro usuário.
        """
        if not email:
            raise ValueError("Email não informado!")

        usuario = UsuarioRepository.obter_usuario_pelo_email(db=db, email=email)

        if usuario and (
            usuario_id_atual is None or usuario.id != usuario_id_atual
        ):
            raise ValueError(
                f"Já existe um usuário cadastrado com o e-mail {email}"
            )

        return True

    @staticmethod
    def verificar_usuario_pelo_id(db: Session, usuario_id: int) -> UsuarioModel:
        """Verifica a existência de um usuário no banco pelo seu ID.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário.

        Returns:
            UsuarioModel: Instância do modelo ORM do usuário encontrado.

        Raises:
            ValueError: Se o usuário não for encontrado no banco de dados.
        """
        usuario = UsuarioRepository.obter_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )

        if not usuario:
            raise ValueError(
                f"Não existe usuário cadastrado com o ID {usuario_id}"
            )
        return usuario

    @staticmethod
    def verificar_usuario_pelo_nome(db: Session, nome: str) -> UsuarioModel:
        """Verifica a existência de um usuário no banco pelo seu nome exacto.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome (str): Nome completo do usuário.

        Returns:
            UsuarioModel: Instância do modelo ORM do usuário encontrado.

        Raises:
            ValueError: Se o usuário não for encontrado pelo nome informado.
        """
        usuario = UsuarioRepository.obter_usuario_pelo_nome(
            db=db, nome_usuario=nome
        )

        if not usuario:
            raise ValueError(
                f"Não encontrado o usuário pelo com o nome {nome}"
            )
        return usuario

    @staticmethod
    def verificar_usuario_pelo_codigo(
        db: Session,
        codigo_usuario: int | None,
        usuario_id_atual: int | None = None,
    ) -> bool | str:
        """Verifica a validade e a disponibilidade de um código/matrícula de usuário.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_usuario (int | None): Código numérico do colaborador a verificar.
            usuario_id_atual (int | None, optional): ID do usuário atual para ignorar no caso de edição.

        Returns:
            bool | str: Retorna `"vazio"` se o código for None ou `True` se estiver disponível.

        Raises:
            ValueError: Se o código já estiver atribuído a outro colaborador.
        """
        if codigo_usuario is None:
            return "vazio"

        usuario = UsuarioRepository.obter_usuario_pelo_codigo(
            db=db, codigo_usuario=codigo_usuario
        )

        if usuario and (
            usuario_id_atual is None or usuario.id != usuario_id_atual
        ):
            raise ValueError(
                f"O código {codigo_usuario} já foi cadastrado para outro usuário!"
            )
        return True

    # ------------------------------- Funções do Sistema -------------------------------

    @staticmethod
    def criar_usuario(
        db: Session, usuario_dados: UsuarioCreate
    ) -> UsuarioResponse:
        """Executa a lógica de criação de um novo usuário com cálculo sequencial do código de colaborador.

        Caso o código não seja informado, calcula automaticamente o próximo número disponível
        com base no maior código cadastrado ou na variável de ambiente `CODIGO_USUARIO_INICIAL`.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_dados (UsuarioCreate): DTO com os dados validados para cadastro.

        Returns:
            UsuarioResponse: DTO contendo os dados do usuário cadastrado.

        Raises:
            ValueError: Se o e-mail ou código informado já estiverem cadastrados.
        """
        UsuarioService.verificar_usuario_pelo_email(
            db=db, email=usuario_dados.email
        )
        codigo_vazio = UsuarioService.verificar_usuario_pelo_codigo(
            db=db, codigo_usuario=usuario_dados.codigo
        )

        usuario_dict = usuario_dados.model_dump()

        if codigo_vazio == "vazio":
            ultimo_codigo = UsuarioRepository.obter_maior_codigo(db=db)
            codigo_inicial_env = int(
                os.getenv("CODIGO_USUARIO_INICIAL", 487)
            )
            if (
                ultimo_codigo is not None
                and ultimo_codigo >= codigo_inicial_env
            ):
                usuario_dict["codigo"] = ultimo_codigo + 1
            else:
                usuario_dict["codigo"] = codigo_inicial_env

        novo_usuario = UsuarioRepository.criar_usuario(
            db=db, dados_usuario=usuario_dict
        )
        return UsuarioResponse.model_validate(novo_usuario)

    @staticmethod
    def alterar_usuario(
        db: Session, usuario_id: int, usuario_dados: UsuarioUpdate
    ) -> UsuarioResponse:
        """Altera os dados cadastrais de um usuário existente verificando conflitos de e-mail.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário a ser alterado.
            usuario_dados (UsuarioUpdate): DTO contendo os novos dados para atualização.

        Returns:
            UsuarioResponse: DTO contendo os dados do usuário atualizado.

        Raises:
            ValueError: Se o usuário não for encontrado ou se o novo e-mail pertencer a outro usuário.
        """
        usuario = UsuarioService.verificar_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )

        usuario_dict = usuario_dados.model_dump(
            exclude_unset=True, exclude={"id"}
        )

        # Valida duplicidade apenas se o e-mail for alterado
        if "email" in usuario_dict and usuario_dict["email"] != usuario.email:
            UsuarioService.verificar_usuario_pelo_email(
                db=db,
                email=usuario_dict["email"],
                usuario_id_atual=usuario_id,
            )

        usuario_atualizado = UsuarioRepository.alterar_usuario(
            db=db, db_usuario=usuario, usuario_dados=usuario_dict
        )
        return UsuarioResponse.model_validate(usuario_atualizado)

    @staticmethod
    def obter_todos_usuarios(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[UsuarioResponse]:
        """Recupera a lista paginada de usuários e converte os registros para DTOs de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros para ignorar (offset). Padrão é 0.
            limit (int, optional): Limite de registros a retornar. Padrão é 100.

        Returns:
            list[UsuarioResponse]: Lista de DTOs dos usuários cadastrados.
        """
        usuarios = UsuarioRepository.obter_todos_usuarios(
            db=db, skip=skip, limit=limit
        )
        return [
            UsuarioResponse.model_validate(usuario)
            for usuario in usuarios
            if usuario is not None
        ]

    @staticmethod
    def obter_usuario_pelo_id(
        db: Session, usuario_id: int
    ) -> UsuarioResponse:
        """Busca um usuário pelo seu ID e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário.

        Returns:
            UsuarioResponse: DTO com os dados do usuário encontrado.

        Raises:
            ValueError: Se o usuário não for encontrado no banco de dados.
        """
        usuario = UsuarioService.verificar_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )
        return UsuarioResponse.model_validate(usuario)

    @staticmethod
    def obter_usuario_pelo_codigo(
        db: Session, codigo_usuario: int
    ) -> UsuarioResponse:
        """Busca um usuário pelo seu código/matrícula e o retorna formatado como DTO.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_usuario (int): Código do colaborador a ser pesquisado.

        Returns:
            UsuarioResponse: DTO com os dados do usuário encontrado.

        Raises:
            ValueError: Se o código fornecido não for encontrado ou pertencer a outro cadastro.
        """
        usuario = UsuarioService.verificar_usuario_pelo_codigo(
            db=db, codigo_usuario=codigo_usuario
        )
        if usuario:
            usuario_pelo_codigo = UsuarioRepository.obter_usuario_pelo_codigo(
                db=db, codigo_usuario=codigo_usuario
            )
            return UsuarioResponse.model_validate(usuario_pelo_codigo)

    @staticmethod
    def obter_usuario_pelo_nome(
        db: Session, nome: str
    ) -> UsuarioResponse:
        """Busca um usuário pelo seu nome completo e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome (str): Nome do colaborador a ser pesquisado.

        Returns:
            UsuarioResponse: DTO com os dados do usuário encontrado.

        Raises:
            ValueError: Se o usuário com o nome informado não for encontrado.
        """
        usuario = UsuarioService.verificar_usuario_pelo_nome(db=db, nome=nome)
        return UsuarioResponse.model_validate(usuario)

    @staticmethod
    def obter_usuario_pelo_email(
        db: Session, email: str
    ) -> UsuarioResponse:
        """Busca um usuário através do seu e-mail e o retorna formatado como DTO de resposta.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            email (str): Endereço de e-mail a ser pesquisado.

        Returns:
            UsuarioResponse: DTO com os dados do usuário encontrado.
        """
        usuario = UsuarioRepository.obter_usuario_pelo_email(db=db, email=email)
        return UsuarioResponse.model_validate(usuario)

    @staticmethod
    def alterar_senha(
        db: Session, usuario_id: int, nova_senha: str
    ) -> UsuarioResponse:
        """Atualiza a senha de acesso de um usuário específico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário.
            nova_senha (str): Nova senha a ser criptografada/salva.

        Returns:
            UsuarioResponse: DTO com os dados do usuário com a senha atualizada.

        Raises:
            ValueError: Se o usuário não for encontrado no banco de dados.
        """
        usuario = UsuarioService.verificar_usuario_pelo_id(
            db=db, usuario_id=usuario_id
        )
        usuario_alterado = UsuarioRepository.alterar_senha(
            db=db, db_usuario=usuario, nova_senha=nova_senha
        )
        return UsuarioResponse.model_validate(usuario_alterado)