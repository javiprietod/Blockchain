# Importamos las librerías necesarias
import json
import hashlib
import time


# Definición de la clase bloque
class Bloque:
    def __init__(self, indice: int, transacciones, timestamp: float, hash_previo: str, prueba: int = 0):
        # Indice del bloque
        self.indice = indice
        # Transacciones que contiene
        self.transacciones = transacciones
        # Momento de creación
        self.timestamp = timestamp
        # Hash del bloque anterior en la cadena
        self.hash_previo = hash_previo
        # Número de veces que se ha calculado el hash hasta que sea correcta
        self.prueba = prueba
        # Hash del bloque
        self.hash = None

    # Calcular el hash del bloque
    def calcular_hash(self) -> str:
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def toDict(bloque):
        '''
        Función que convierte un bloque en un diccionario
        '''
        return bloque.__dict__

# Creación de la clase Blockchain
class Blockchain(object):

    def __init__(self):
        # Número de 0's necesarios al comienzo del hash
        self.dificultad = 4
        # Lista de transacciones sin confirmar (sin añadir a un bloque)
        self.transacciones = []
        # Cadena de todos los bloques
        self.cadena = []
        # Último bloque de la cadena
        self.anterior = self.primer_bloque()

    def primer_bloque(self) -> Bloque:
        '''
        Función que crea el primer bloque de la cadena
        y lo añade a la cadena de bloques. Este bloque
        comienza siendo el anterior
        '''
        bloque = Bloque(1, [], 0, "0", 0)
        hash_1 = bloque.calcular_hash()
        bloque.hash = hash_1
        self.cadena.append(bloque)
        return bloque

    def nuevo_bloque(self, hash_previo: str) -> Bloque:
        ''' Crea un nuevo bloque a partir de las transacciones que no estan
            confirmadas
            :param prueba: el valor de prueba a insertar en el bloque
            :param hash_previo: el hash del bloque anterior de la cadena
            :return: el nuevo bloque
        '''
        # Hash_previo = hash del último bloque de la cadena confiramda
        self.anterior.hash = hash_previo
        # El índice es uno más que el último de la cadena y su hash comienza como 0
        bloque = Bloque(self.anterior.indice+1, self.transacciones, time.time(), hash_previo, 0)
        return bloque

    def nueva_transaccion(self, origen: str, destino: str, cantidad: int) -> int:
        '''
        Función que añade una transacción a la lista de transacciones sin confirmar y devuelve
        el índice del bloque en el que se va a integrar dicha transacción. Ese índice
        será uno más que el índice del último bloque confirmado
        '''
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
        # Primer hash
        hash_prueba = bloque.calcular_hash()
        # Vuelve a calcularlo, incrementando en uno el valor de prueba hasta 
        # que sea válido
        while hash_prueba[0:self.dificultad] != "0"*self.dificultad:
            bloque.prueba += 1
            hash_prueba = bloque.calcular_hash()

        # Hash válido calculado
        return hash_prueba

    # def dificultad_adecuada(self, hash_prueba):
    #     '''
    #     Función que comprueba si un hash comienza por tantos
    #     ceros como indique la dificultad
    #     '''
    #     return 

    def prueba_valida(self, bloque: Bloque, hash_bloque: str) -> bool:
        '''
        Metodo que comprueba si el hash_bloque comienza con tantos ceros como
        la dificultad estipulada en el blockchain
        Ademas comprobara que hash_bloque coincide con el valor devuelvo del
        metodo de calcular hash del bloque.
        Si cualquiera de ambas comprobaciones es falsa, devolvera falso y en
        caso contrario, verdarero
        :param bloque:
        :param hash_bloque:
        :return:
        '''
        return hash_bloque == bloque.calcular_hash() and hash_bloque[0:self.dificultad] == "0"*self.dificultad

    def integra_bloque(self, bloque_nuevo: Bloque, hash_prueba: str) -> bool:
        """
        Metodo para integran correctamente un bloque a la cadena de bloques.
        Debe comprobar que la prueba de hash es valida y que el hash del bloque
        ultimo de la cadena
        coincida con el hash_previo del bloque que se va a integrar. Si pasa
        las comprobaciones, actualiza el hash
        del bloque a integrar, lo inserta en la cadena y hace un reset de las
        transacciones no confirmadas (
        vuelve
        a dejar la lista de transacciones no confirmadas a una lista vacia)
        :param bloque_nuevo: el nuevo bloque que se va a integrar
        :param hash_prueba: la prueba de hash
        :return: True si se ha podido ejecutar bien y False en caso contrario
        (si no ha pasado alguna prueba)
        """
        # Comprueba que el hash previo coincide
        if bloque_nuevo.hash_previo != self.anterior.hash:
            return "No valido previo"


        # Comprueba que el hash dado sea el correcto
        if not self.prueba_valida(bloque_nuevo, hash_prueba):
            return "No hash valido"

        
        # Si todo es correcto, actualiza el hash
        bloque_nuevo.hash = hash_prueba

        # Añade el bloque a la lista de bloques confirmados
        self.cadena.append(bloque_nuevo)

        # Vacía la lista de transacciones sin confirmar
        self.transacciones = []

        # El nuevo último bloque de la cadena será el que 
        # acabamos de añadir
        self.anterior = bloque_nuevo

        return True
