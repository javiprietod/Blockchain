# Importamos las librerías necesarias
import Blockchain
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from threading import Semaphore, Thread
import time
import datetime
import json
import platform
import requests

# Semáforo para controlar el acceso a la zona crítica
# (cadena de bloques)
mutex = Semaphore(1)

# Instancia del nodo
app = Flask(__name__)

# Instanciacion de la aplicacion
blockchain = Blockchain.Blockchain()

# Lista con los nodos que hay en la red
nodos_red = []

# Para saber mi ip
mi_ip = socket.gethostbyname(socket.gethostbyname('localhost'))


def copia_seguridad(puerto: int):
    '''
    Función que realiza una copia de seguridad del nodo actual
    y la guarda en un fichero que contiene el id del nodo,
    así como el puerto en el que se realizan las operaciones
    '''
    # Nombre del fichero sobre el que vamos a escribir
    copia = f'respaldo-nodo{mi_ip}-{puerto}.json'

    # Realiza la copia de seguridad cada 60 segundos hasta que se termina
    # el programa
    while True:
        # Contenido a escribir en el fichero
        response = {
            'chain': [b.__dict__ for b in blockchain.cadena if b.hash is not None],
            'longitud': len(blockchain.cadena),
            'date': datetime.date.today()
            }
        # Abrimos el fichero y escribimos
        with open(copia, 'w') as file:

            # Para evitar que se modifique la cadena mientras
            # se hace la copia de seguridad
            mutex.acquire()

            # Escribimos lo necesario
            json.dump(response, file, default=str, indent=1)

            # Cerramos el fichero para cargar bien los datos
            file.close()

            # Ya se puede modificar la cadena
            mutex.release()

            # Dormimos el tiempo estipulado entre copias de seguridad
            time.sleep(60)


def actualizar_blockchain(data: list):
    '''
    Función que actualiza blockchain con la cadena recibida en lista
    '''

    # Objeto Blockchain que empieza vacío en el que aparecerán los datos
    # leidos en data
    blockchain_leida = Blockchain.Blockchain()

    # Creamos el primer bloque
    primero = Blockchain.Bloque(data[0]['indice'], data[0]['transacciones'], data[0]['timestamp'], data[0]['hash_previo'], data[0]['prueba'])
    primero.timestamp = data[0]['timestamp']
    primero.hash = data[0]['hash']

    # Establecemos en la cadena y como el anterior
    # el primer bloque para evitar errores
    blockchain_leida.cadena = [primero]
    blockchain_leida.anterior = primero

    # Añadimos el resto de los bloques de forma normal
    for i in range(1, len(data)):
        bloque_nuevo = Blockchain.Bloque(data[i]['indice'], data[i]['transacciones'], data[i]['timestamp'], data[i]['hash_previo'], data[i]['prueba'])

        # Vemos si se puede integrar
        valido = blockchain_leida.integra_bloque(bloque_nuevo, data[i]['hash'])

        # Si no, es que la cadena está corrupta y devuelve una
        # blockhain vacía (None)
        if not valido:
            blockchain_leida = None
            break

    # Devuelve la blockchain que hemos creado
    return blockchain_leida


@app.route('/system', methods=['GET'])
def system():
    '''
    Función que, al realizar el método GET,
    devuelve la máquina, el nombre del sistema utilizado
    y su versión, haciendo uso de la librería platform
    '''
    response = {
            'maquina': platform.machine(),
            'nombre_sistema': platform.system(),
            'version': platform.version(),
            }
    # El código 201 indica que todo ha funcionado correctamente
    return jsonify(response), 201


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    '''
    Función que añade una transación a la lista de transacciones
    sin confirmar de blockchain al usar el método "POST"
    '''
    # Coge los valores del JSON que se ha introducido con la petición
    values = request.get_json()

    # Comprobamos que están todos los datos de la transaccion
    required = ['origen', 'destino', 'cantidad']

    if not all(k in values for k in required):
        # En caso de que no estén, devuelven un mensaje de error y
        # el código de error correspondiente
        return 'Faltan valores', 400

    # Creamos una nueva transaccion aquí, con los valores dados por el
    # usuario y la función nueva_transacción de Blockchain.py
    index = blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])

    # Una vez se ha realizado la operación, se imprime un mensaje
    # confirmado la acción y en el que se indica el índice del bloque
    #  en el que se añadirá la transacción
    # (devuelto por blockchain.transaccion)
    response = {'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}

    # Da la respuesta en el formato correspondiente con su código asociado
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    '''
    Función que devuelve toda la cadena de bloques
    que se han realizado, especificando los detalles de cada bloque
    al usar 'GET'.
    '''
    response = {
        'chain': [b.toDict() for b in blockchain.cadena if b.hash is not None],
        'longitud': len(blockchain.cadena)
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    global blockchain
    '''
    Función que mina un bloque que tiene como transacciones las transacciones
    sin confirmar que contenga el objeto blockchain
    '''
    # Si no hay transacciones no se puede minar un nuevo bloque
    if len(blockchain.transacciones) == 0:
        response = {
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }

    elif not resuelve_conflictos():
        # Si hay un conflicto, no se puede minar un nuevo bloque,
        # si no que se sustituye la cadena por la cadena del nodo
        # que tenga la cadena más larga
        response = {'mensaje': "Ha habido un conflicto. Esta cadena se ha actualizado con una version mas larga"}

        # Longitud de la cadena actual
        longitud_actual = len(blockchain.cadena)

        # Buscamos la cadena mas larga
        for nodo in nodos_red:
            # Buscamos la longitud con 'chain'
            cadena_nodo = requests.get(str(nodo) + '/chain').json()
            if cadena_nodo.get('longitud') > longitud_actual:
                nodo_mayor = nodo

        # Actualizamos la cadena del nodo a la cadena mas larga
        data = requests.get(str(nodo_mayor) +'/chain').json().get('chain')
        blockchain = actualizar_blockchain(data)

    else:
        # En caso de que sí haya transacciones, se mina el bloque
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos
        # recompensa
        # Guardamos el hash del bloque anterior de la cadena
        previous_hash = blockchain.anterior.hash

        # Recibimos un pago por minar el bloque.
        # Creamos una nueva transaccion con:
        # Dejamos como origen el 0
        # Destino nuestra ip
        # Cantidad = 1
        blockchain.nueva_transaccion("0", mi_ip, 1)

        # Creamos un nuevo bloque, a continuación del último que
        # había en la cadena
        bloque_nuevo = blockchain.nuevo_bloque(previous_hash)

        # Calculamos el hash y actualizamos el valor del
        # campo prueba del bloque
        hash_prueba = blockchain.prueba_trabajo(bloque_nuevo)

        # Para evitar que se realice una copia de seguridad
        # si se está modificando la cadena
        mutex.acquire()

        # Vemos si se puede integrar correctamente el bloque a la cadena
        if blockchain.integra_bloque(bloque_nuevo, hash_prueba):

            # Si es el caso, se inttegra en la función correctamente
            # y se crea un mensaje con los detalles
            response = {
                'mensaje': "Nuevo bloque minado",
                "id": bloque_nuevo.indice,
                "transacciones": bloque_nuevo.transacciones,
                "prueba": bloque_nuevo.prueba,
                "hash previo": previous_hash,
                "hash": bloque_nuevo.hash,
                "timestamp": bloque_nuevo.timestamp
            }
        else:
            # Si no se ha podido integrar a la cadena, devuelve un
            # mensaje de error
            response = {'mensaje': 'No se puede minar nuevo bloque'}

        # Ya se puede hacer la copia de seguridad
        mutex.release()

    # Devuelve el código y el mensaje adecuados
    return jsonify(response), 200


@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    '''
    Función que registra varios nodos en la red
    '''
    values = request.get_json()
    global blockchain
    global nodos_red

    # Nodos nuevos a añadir a la red
    nodos_nuevos = values.get('direccion_nodos')

    # Si no hay nodo a añadir, no se añaden
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400

    # Variable para verificar que todo funciona según lo previsto
    all_correct = True

    # Almacenamos nuestra ip en una lista para luego poder
    # sumarla a la lista de nodos
    mi_nodo = [f'http://{mi_ip}:{puerto}']

    # Comprobamos que en los nodos nuevos no esté nuestra ip
    nodos_nuevos.remove(mi_nodo) if mi_nodo in nodos_nuevos else None

    # Añadimos los nodos nuevos a la lista de nodos
    for nodo in nodos_nuevos:
        nodos_red.append(nodo) if nodo not in nodos_red else None

    # Introducimos los nodos nuevos en nuestra red de blockchain
    for nodo in nodos_red:

        # Lista de nodos a añadir en cada nodo, es la lista de todos
        # menos a sí mismo
        temp = nodos_red.copy()
        temp.remove(nodo)

        # Datos que tiene que tener ese nodo
        data = {'nodos_direcciones': temp + mi_nodo, 'blockchain': {'chain': [b.toDict() for b in blockchain.cadena if b.hash is not None]}}

        # Tratamos de registrar un nodo concreto
        response = requests.post(nodo+"/nodos/registro_simple", data=json.dumps(data), headers ={'Content-Type' : "application/json"})

        # Si ha dado un error, all_correct pasa a ser False
        if response.status_code == 400:
            all_correct = False

    # Si todo ha ido correctamente, se devuelve el mensaje de confirmación
    if all_correct:
        response = {
                    'mensaje': 'Se han incluido nuevos nodos en la red',
                    'nodos_totales': list(nodos_red)
        }

    # En caso de que haya habido algún error, se devuelve el
    # mensaje correspondiente
    else:
        response = {
                    'mensaje': 'Error notificando el nodo estipulado',
        }

    # Devolvemos la respuesta que se haya generado
    return jsonify(response), 201


@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    '''
    Función que registra un nodo y actualiza el blockchain
    de dicho nodo
    '''
    # Obtenemos la variable global de blockchain
    global blockchain
    read_json = request.get_json()
    # Obtenemos la lista de nodos a añadir
    nodes_addreses = read_json.get("nodos_direcciones")

    # Actualizamos la lista de nodos con los nodos introducidos en la peticion
    for nodo in nodes_addreses:
        nodos_red.append(nodo) if nodo not in nodos_red else None

    # Actualizamos la blockchain con la blockchain introducida en la peticion
    data = read_json.get("blockchain")
    data = data['chain']
    blockchain_leida = actualizar_blockchain(data)

    # Si ha dado un error, es porque se ha corrompido la cadena
    if blockchain_leida == 1:
        return "El blockchain de la red esta currupto", 400

    else:
        # En caso de que todo funcione correctamente
        # Actualizamos la blockchain
        blockchain = blockchain_leida

    # Si todo ha funcionado según lo esperado, devuelve un
    # mensaje de confirmación
    return "La blockchain del nodo" + str(mi_ip) + ":" + str(puerto) + "ha sido correctamente actualizada", 200


def resuelve_conflictos():
    '''
    Función que comprueba si se pueden minar o no los bloques,
    es decir, si hay algún nodo que tenga una cadena más larga
    que la cadena del nodo que está intentando minar un bloque
    '''
    global blockchain
    global nodos_red

    # Longitud del nodo actual
    longitud_actual = len(blockchain.cadena)

   # Comprobamos si la cadena de alguno de los nodos
   # es más larga que la nuestra
   # Si es así, devolvemos False para
   #  más tarde actualizamos la nuestra
    for nodo in nodos_red:
        # Calculamos la longitud del resto de cadenas
        response = requests.get(str(nodo) + '/chain').json()

        # Comprobamos si es mayor a la actual
        if response.get('longitud') > longitud_actual:
            return False

    return True


if __name__ == '__main__':
    '''
    Main del programa
    '''

    # Inicio del programa
    parser = ArgumentParser()
    puerto = input()
    parser.add_argument('-p', '--puerto', default=puerto, type=int, help='puerto para escuchar')
    args = parser.parse_args()
    puerto = args.puerto

    # Creación del hilo que realiza la copia de seguridad cada 60 segundos
    copia_de_seguridad = Thread(target=copia_seguridad, args=(puerto,))

    # Iniciamos el hilo
    copia_de_seguridad.start()

    # Iniciamos la aplicación
    app.run(host='0.0.0.0', port=puerto)

    # Finalización del hilo de la copia de seguridad
    copia_de_seguridad.join()
