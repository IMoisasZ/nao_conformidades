class TratamentoDados:
    def __init__(self, value:str, name_value:str, min_length:int = 2):
        self.value = value.upper() if value is not None else "" 
        self.name_value = name_value
        self.min_length = min_length
        self.cleaned_value = self.value.strip()
        
    def valor_vazio(self):
        if not self.value or not self.cleaned_value:
            raise ValueError(f"O {self.name_value} deve ser informado")
        return self.cleaned_value
        
    def validacao(self):
        if not self.cleaned_value or len(self.cleaned_value) < self.min_length:
            raise ValueError(f"O campo {self.name_value} deve ter no minimo {self.min_length} caracteres!")
        return self.cleaned_value

    def validar_e_limpar(self) -> str:
        self.valor_vazio()
        self.validacao()

        return self.cleaned_value    