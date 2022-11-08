import BlockChain
from uuid import uuid4
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
# Instancia del nodo
app = Flask(__name__)
# Instanciacion de la aplicacion
blockchain =BlockChain.Blockchain()
# Para saber mi ip
mi_ip =socket.gethostbyname(socket.gethostname())
if __name__ =='__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    app.run(host='0.0.0.0', port=puerto)