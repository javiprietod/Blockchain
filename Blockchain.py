import time
class Blockchain(object):

    def __init__(self):
        self.dificultad = 4
        self.anterior = None
        self.transacciones = None

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