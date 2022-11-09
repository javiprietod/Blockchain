import BlockChain
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

# Semáforo para controlar el acceso a la zona crítica 
# (cadena de bloques)
mutex = Semaphore(1)

# Instancia del nodo
app = Flask(__name__)

# Instanciacion de la aplicacion
blockchain = BlockChain.Blockchain()

# Para saber mi ip
mi_ip = socket.gethostbyname(socket.gethostname())


def copia_seguridad(puerto):
    copia = f'respaldo-nodo{mi_ip}-{puerto}.json'
    while True:
        response = {
            'chain': [b.__dict__ for b in blockchain.cadena if b.hash is not None],
            'longitud': len(blockchain.cadena),
            'date': datetime.date.today()
            }
        os.remove(copia)
        with open(copia, 'a') as file:
            # mutex.acquire()
            # file.write("a")
            json.dump(response, file, default=str, indent=1)
            # mutex.release()
            time.sleep(5)
            file.close()


@app.route('/system', methods=['GET'])
def system():
    response = {
            'maquina': platform.machine(),
            'nombre_sistema': platform.system(),
            'version': platform.version(),
            }
    return jsonify(response), 201


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values = request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required = ['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    index = blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])
    response = {'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response = {
        'chain': [b.__dict__ for b in blockchain.cadena if b.hash is not None],
        'longitud': len(blockchain.cadena)
    }
    return jsonify(response), 200


@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones

    if len(blockchain.transacciones) == 0:

        response = {
            'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos
        # recompensa
        previous_hash = blockchain.anterior.hash
        blockchain.nueva_transaccion("0", mi_ip, 1)
        bloque_nuevo = blockchain.nuevo_bloque(previous_hash)
        hash_prueba = blockchain.prueba_trabajo(bloque_nuevo)
        mutex.acquire()
        if blockchain.integra_bloque(bloque_nuevo, hash_prueba):
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
            response = {'mensaje': 'No se puede minar nuevo bloque'}
        mutex.release()

    # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
    # Dejamos como origen el 0
    # Destino nuestra ip
    # Cantidad = 1
    # [Completar el siguiente codigo]
    return jsonify(response), 200



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')
    args = parser.parse_args()
    puerto = args.puerto
    copia_de_seguridad = Thread(target=copia_seguridad, args=(puerto,))
    copia_de_seguridad.start()
    app.run(host='0.0.0.0', port=puerto)
    copia_de_seguridad.join()
