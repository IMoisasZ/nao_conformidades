class TratamentoNumeroCaracteres:
    @staticmethod
    def qtde_caracteres(senha:str = None, num_caracteres:int = 3) -> int:
        qtde_caractres_senha = len(senha.strip())
        if qtde_caractres_senha < num_caracteres:
            return False
        return True
            
        