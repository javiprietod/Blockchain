import BlockChain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
# Instancia del nodo
app = Flask(__name__)
# Instanciacion de la aplicacion
blockchain =BlockChain.Blockchain()

@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values = request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required =['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    index = blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])
    response ={'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response ={
    # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
    'chain': [b.toDict() for b in blockchain.cadena if b.hash is not None],
    'longitud': len(blockchain.cadena)
    }
    return jsonify(response), 200

@app.route('/minar', methods=['GET'])
def minar():
    # No hay transacciones
    if len(blockchain.transacciones) ==0:
        response ={
        'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # Hay transaccion, por lo tanto ademas de minear el bloque, recibimos recompensa
        previous_hash =blockchain.last_block.hash
        blockchain.nueva_transaccion("0", mi_ip, 1)
        blockchain.nuevo_bloque(previous_hash)
        response ={
        'mensaje': "Nuevo bloque minado"
        }




    # Recibimos un pago por minar el bloque. Creamos una nueva transaccion con:
    # Dejamos como origen el 0
    # Destino nuestra ip
    # Cantidad = 1
    # [Completar el siguiente codigo]






    return jsonify(response), 200


# Para saber mi ip
mi_ip =socket.gethostbyname(socket.gethostname())


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values =request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required =['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    index =blockchain.nueva_transaccion(values.origen, values.destino, values.cantidad)
    response = {'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response ={
    # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
    'chain': [b.toDict() for b in blockchain.chain if b.hash is not None],
    'longitud': len(blockchain.cadena)
    }
    return jsonify(response), 200
if __name__ =='__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    app.run(host='0.0.0.0', port=puerto)