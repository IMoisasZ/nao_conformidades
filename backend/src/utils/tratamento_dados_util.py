"""Módulo de Utilitários para Tratamento e Validação de Dados de Texto.

Este módulo contém a classe `TratamentoDados`, responsável por padronizar
a higienização (caixa alta, remoção de espaços nas extremidades) e a validação
de presença e tamanho mínimo para entradas de texto no sistema.
"""


class TratamentoDados:
    """Classe utilitária para higienização e validação de strings.

    Realiza a conversão de textos para caixa alta (`UPPERCASE`), remoção de espaços
    sobressalentes nas extremidades (`strip`) e validações de preenchimento obrigatório
    e comprimento mínimo.

    Attributes:
        value (str): Texto original convertido em caixa alta (ou string vazia caso `None`).
        name_value (str): Nome amigável do campo a ser exibido nas mensagens de erro.
        min_length (int): Quantidade mínima de caracteres exigida para o texto.
        cleaned_value (str): Texto sem espaços em branco nas extremidades.
    """

    def __init__(self, value: str, name_value: str, min_length: int = 2):
        """Inicializa os atributos de tratamento do texto fornecido.

        Args:
            value (str): String a ser tratada e validada.
            name_value (str): Rótulo/Nome do campo para formatação de exceções.
            min_length (int, optional): Tamanho mínimo aceito. Padrão é 2.
        """
        self.value = value.upper() if value is not None else ""
        self.name_value = name_value
        self.min_length = min_length
        self.cleaned_value = self.value.strip()

    def valor_vazio(self) -> str:
        """Valida se a string não está vazia ou composta apenas por espaços.

        Returns:
            str: O valor limpo sem espaços nas extremidades.

        Raises:
            ValueError: Se o valor for vazio ou nulo.
        """
        if not self.value or not self.cleaned_value:
            raise ValueError(f"O {self.name_value} deve ser informado")
        return self.cleaned_value

    def validacao(self) -> str:
        """Valida se a quantidade de caracteres atende ao tamanho mínimo configurado.

        Returns:
            str: O valor limpo sem espaços nas extremidades.

        Raises:
            ValueError: Se o tamanho da string for inferior ao atributo `min_length`.
        """
        if not self.cleaned_value or len(self.cleaned_value) < self.min_length:
            raise ValueError(
                f"O campo {self.name_value} deve ter no mínimo {self.min_length} caracteres!"
            )
        return self.cleaned_value

    def validar_e_limpar(self) -> str:
        """Executa a sequência completa de validações (presença e comprimento) e retorna o texto limpo.

        Returns:
            str: Texto higienizado em caixa alta e sem espaços nas extremidades.

        Raises:
            ValueError: Se qualquer uma das etapas de validação falhar.
        """
        self.valor_vazio()
        self.validacao()

        return self.cleaned_value