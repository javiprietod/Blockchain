# Importamos las librerías necesarias
import Blockchain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from threading import Semaphore, Thread
import time
import datetime
import json
import os
import platform
import requests

# Semáforo para controlar el acceso a la zona crítica 
# (cadena de bloques)
mutex = Semaphore(1)

# Instancia del nodo
app = Flask(__name__)

# Instanciacion de la aplicacion
blockchain = Blockchain.Blockchain()
nodos_red = []
# Para saber mi ip
mi_ip = socket.gethostbyname(socket.gethostbyname('localhost'))



def copia_seguridad(puerto):
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
            mutex.acquire()
            # Escribimos lo necesario
            json.dump(response, file, default=str, indent=1)
            # Dormimos el tiempo estipulado entre copias de seguridad
            file.close()
            mutex.release()
            time.sleep(5)
            

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

    # Una vez se ha realizado la operación, se imprime un mensaje confirmado la acción
    # y en el que se indica el índice del bloque en el que se añadirá la transacción
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
        'chain': [b.__dict__ for b in blockchain.cadena if b.hash is not None],
        'longitud': len(blockchain.cadena)
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    '''
    Función que mina un bloque que tiene como transacciones las transacciones
    sin confirmar que contenga el objeto blockchain
    '''
    # Si no hay transacciones no se puede minar un nuevo bloque
    if len(blockchain.transacciones) == 0:

        response = {
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    
    # En caso de que sí haya transacciones, se mina el bloque
    else:
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos
        # recompensa

        # Guardamos el hash del bloque anterior de la cadena
        previous_hash = blockchain.anterior.hash

        # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
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
    values = request.get_json()
    global blockchain
    global nodos_red
    nodos_nuevos =values.get('direccion_nodos')
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400
    all_correct =True
    #[Codigo a desarrollar]

    for nodo in nodos_nuevos:
        nodos_red.append(nodo)

    response =requests.post(nodo+"/nodos/registro_simple", data=json.dumps(data), headers ={'Content-Type':"application/json"})
    if response.status_code() == 400:
        all_correct = False
    # Fin codigo a desarrollar
    if all_correct:
        response ={
        'mensaje': 'Se han incluido nuevos nodos en la red',
        'nodos_totales': list(nodos_red)
        }
    else:
        response ={
        'mensaje': 'Error notificando el nodo estipulado',
        }
    return jsonify(response), 201


@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    # Obtenemos la variable global de blockchain
    global blockchain
    read_json = request.get_json()
    nodes_addreses = read_json.get("nodos_direcciones")
    # [...] Codigo a desarrollar


    response =requests.post(nodo+"/nodos/registro_simple", data=json.dumps(data), headers ={'Content-Type':"application/json"})


    #[...] fin del codigo a desarrollar
    if blockchain_leida is None:
        return "El blockchain de la red esta currupto", 400
    else:
        blockchain =blockchain_leida
    return "La blockchain del nodo" +str(mi_ip) +":" +str(puerto) +"ha sido correctamente actualizada", 200


if __name__ == '__main__':
    '''
    Main principal del programa
    '''
    parser = ArgumentParser()
    
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')
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
