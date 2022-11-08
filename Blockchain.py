import json
import hashlib

class Bloque:
    def __init__(self, indice: int, transacciones: list[dict], timestamp: float, hash_previo: str, prueba: int =0):
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.prueba = prueba
        self.hash = self.calcular_hash()
    # Codigo a completar (inicializacion de los elementos del bloque)
    def calcular_hash(self) -> str:
        block_string =json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()