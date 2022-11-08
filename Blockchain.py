import json
import hashlib
import time

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

class Blockchain(object):

    def __init__(self):
        self.dificultad = 4
        self.anterior = self.primer_bloque()
        self.transacciones = None

    def primer_bloque(self) ->Bloque:
        return Bloque(1, [], 0, "1", 0)

    def nuevo_bloque(self, hash_previo: str) ->Bloque:
        ''' Crea un nuevo bloque a partir de las transacciones que no estan
            confirmadas
            :param prueba: el valor de prueba a insertar en el bloque
            :param hash_previo: el hash del bloque anterior de la cadena
            :return: el nuevo gloque
        '''
        hash_previo = self.anterior.hash
        prueba = self.prueba_trabajo(bloque)

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        transaccion = {"origen": origen, "destino": destino, "cantidad": cantidad, "tiempo": time.time()}
        self.transacciones.append(transaccion)
        pass

    def prueba_trabajo(self, bloque: Bloque) ->str:
        prueba_del_bloque = 0
        hash_prueba = bloque.calcular_hash()
        while not self.prueba_valida(bloque,hash_prueba):
            prueba_del_bloque += 1
            hash_prueba = bloque.calcular_hash
        pass

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) ->bool:
        pass

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) ->bool:
        pass
