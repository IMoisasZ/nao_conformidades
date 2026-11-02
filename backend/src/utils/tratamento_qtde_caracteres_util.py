"""Módulo de Utilitários para Validação da Quantidade de Caracteres.

Este módulo contém a classe `TratamentoNumeroCaracteres`, responsável por verificar
se credenciais ou textos atingem a quantidade mínima de caracteres exigida pelo sistema.
"""

from typing import Optional


class TratamentoNumeroCaracteres:
    """Classe utilitária para validação do comprimento de senhas e dados textuais."""

    @staticmethod
    def qtde_caracteres(senha: Optional[str] = None, num_caracteres: int = 3) -> bool:
        """Verifica se a senha fornecida atinge o número mínimo de caracteres exigido após remoção de espaços.

        Args:
            senha (Optional[str], optional): String contendo a senha a ser validada. Padrão é None.
            num_caracteres (int, optional): Quantidade mínima exigida de caracteres. Padrão é 3.

        Returns:
            bool: Retorna `True` caso a senha possua um comprimento igual ou maior ao mínimo estipulado,
                ou `False` caso contrário.
        """
        senha_limpa = (senha or "").strip()
        qtde_caracteres_senha = len(senha_limpa)

        if qtde_caracteres_senha < num_caracteres:
            return False
        return True