"""Módulo de Definição do Modelo de Vínculo entre Usuários e Setores.

Este módulo contém a entidade ORM (UsuarioSetorModel) que gerencia a tabela pivô
de associação muitos-para-muitos (N:N) entre a tabela de usuários e a de setores.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.src.connection.db_connection import Base


class UsuarioSetorModel(Base):
    """Modelo ORM representando a tabela pivô de relacionamento entre usuários e setores (`usuarios_setores`).

    Esta classe define a estrutura de associação N:N entre as entidades `UsuarioModel` e `SetorModel`,
    incluindo restrição de unicidade para evitar associações duplicadas, exclusão em cascata
    e propriedades auxiliares para acesso facilitado a dados das tabelas relacionadas.

    Attributes:
        id (int): Chave primária autoincrementável da relação.
        usuario_id (int): Chave estrangeira que referencia a chave primária `id` na tabela `usuarios`.
            Possui remoção em cascata (`CASCADE`).
        setor_id (int): Chave estrangeira que referencia a chave primária `id` na tabela `setores`.
            Possui remoção em cascata (`CASCADE`).
        created_at (datetime): Data e hora UTC da criação do registro de vínculo.
        updated_at (datetime): Data e hora UTC da última alteração do registro de vínculo.
        usuario (relationship): Relacionamento ORM de N:1 apontando para a entidade `UsuarioModel`.
        setor (relationship): Relacionamento ORM de N:1 apontando para a entidade `SetorModel`.
    """

    __tablename__ = "usuarios_setores"

    id = Column(Integer, primary_key=True, autoincrement=True)

    usuario_id = Column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    setor_id = Column(
        Integer, ForeignKey("setores.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Restrição de unicidade para impedir a criação de duplicidades do mesmo par (usuário, setor)
    __table_args__ = (
        UniqueConstraint("usuario_id", "setor_id", name="uq_usuario_setor"),
    )

    # Relacionamentos ORM
    usuario = relationship("UsuarioModel", back_populates="setores_vinculados")
    setor = relationship("SetorModel", back_populates="usuarios_vinculados")

    @property
    def nome_usuario(self) -> str:
        """Obtém o nome do usuário associado através do relacionamento.

        Returns:
            str: Nome do usuário cadastrado ou string vazia caso o relacionamento seja nulo.
        """
        return self.usuario.nome if self.usuario else ""

    @property
    def nome_setor(self) -> str:
        """Obtém o nome do setor associado através do relacionamento.

        Returns:
            str: Nome do setor cadastrado ou string vazia caso o relacionamento seja nulo.
        """
        return self.setor.nome_setor if self.setor else ""

    def to_dict(self) -> dict:
        """Converte o objeto `UsuarioSetorModel` em um dicionário formatado.

        Utilizado para facilitar a serialização e exibição em tabelas/dataframes da interface gráfica.

        Returns:
            dict: Dicionário contendo os dados do relacionamento com rótulos amigáveis:
                - "id" (int): Identificador do registro de vínculo.
                - "Usuario ID" (int): Chave primária do usuário.
                - "Nome Usuario" (str): Nome do colaborador.
                - "Setor ID" (int): Chave primária do setor.
                - "Nome Setor" (str): Nome do setor sob responsabilidade.
        """
        return {
            "id": self.id,
            "Usuario ID": self.usuario_id,
            "Nome Usuario": self.nome_usuario,
            "Setor ID": self.setor_id,
            "Nome Setor": self.nome_setor,
        }