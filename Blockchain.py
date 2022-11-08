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

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        ''' Crea un nuevo bloque a partir de las transacciones que no estan
            confirmadas
            :param prueba: el valor de prueba a insertar en el bloque
            :param hash_previo: el hash del bloque anterior de la cadena
            :return: el nuevo bloque
        '''
        bloque = Bloque(self.anterior.indice+1, [], time.time(), hash_previo, 0)
        self.anterior = bloque
        hash_previo = self.anterior.hash
        prueba = self.prueba_trabajo(bloque)
        return bloque

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        transaccion = {"origen": origen, "destino": destino, "cantidad": cantidad, "tiempo": time.time()}
        self.transacciones.append(transaccion)
        return self.anterior.indice + 1

    def prueba_trabajo(self, bloque: Bloque) ->str:
        '''Algoritmo simple de prueba de trabajo:
            - Calculara el hash del bloque hasta que encuentre un hash que empiece
            por tantos ceros como dificultad
            - Cada vez que el bloque obtenga un hash que no sea adecuado,
            incrementara en uno el campo de
            ``prueba del bloque''
            :param bloque: objeto de tipo bloque
            :return: el hash del nuevo bloque (dejara el campo de hash del bloque sin
            modificar)
            '''
        prueba_del_bloque = 0
        hash_prueba = bloque.calcular_hash()
        while not self.dificultad_adecuada(hash_prueba):
            prueba_del_bloque += 1
            hash_prueba = bloque.calcular_hash()
        return hash_prueba

    def dificultad_adecuada(self,hash_prueba):
        for i in range(0, self.dificultad):
                if hash_prueba[i] != 0:
                    return False
        return True

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) ->bool:
        '''
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como la
        dificultad estipulada en el
        blockchain
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del
        bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en caso
        contrario, verdarero
        :param bloque:
        :param hash_bloque:
        :return:
        '''
        if hash_bloque == bloque.hash():
            for i in range(0, self.dificultad):
                if hash_bloque[i] != 0:
                    return False
            return True
        else:
            return False

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) ->bool:
        pass
