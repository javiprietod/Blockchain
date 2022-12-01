import requests
import json

# Cabecera JSON (comun a todas)
cabecera = {'Content-type': 'application/json', 'Accept': 'text/plain'}

#  NUEVA TRANSACCIÓN
# Datos transaccion
transaccion_nueva = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
# Petición para añadir la transacción a la lista de transacciones sin confirmar
r = requests.post('http://127.0.0.1:5000/transacciones/nueva', data=json.dumps(
			transaccion_nueva), headers=cabecera)
# Imprimir el texto que devuelve esa operación
print(r.text)

# MINAR UN BLOQUE
r = requests.get('http://127.0.0.1:5000/minar')
print(r.text)

# IMPRIMIR LA CADENA CREADA
r = requests.get('http://127.0.0.1:5000/chain')
print(r.text)

# REGISTRAR NUEVOS NODOS A LA RED
nodos_a_registrar = {
					"direccion_nodos": ['http://127.0.0.1:5001', 'http://127.0.0.1:5002']
}

r = requests.post('http://127.0.0.1:5000/nodos/registrar', data=json.dumps(nodos_a_registrar), headers=cabecera)
print(r.text)

# AÑADIR UNA TRANSACCIÓN NUEVA EN EL NODO 5000
transaccion_nueva = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r = requests.post('http://127.0.0.1:5000/transacciones/nueva', data=json.dumps(
                   transaccion_nueva), headers=cabecera)
print(r.text)

# MINAR UN BLOQUE EN EL NODO 5000
r = requests.get('http://127.0.0.1:5000/minar')
print(r.text)

# AÑADIR UNA TRANSACCIÓN EN EL NODO 5001
transaccion_nueva = {'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r = requests.post('http://127.0.0.1:5001/transacciones/nueva', data=json.dumps(
                   transaccion_nueva), headers=cabecera)
print(r.text)

# IMPRIMR LA CADENA DEL NODO 5001
r = requests.get('http://127.0.0.1:5001/chain')
print(r.text)

# TRATAMOS DE MINAR UN BLOQUE EN EL NODO 5001
# PARA VER QUE HAY CONFLICTOS
r = requests.get('http://127.0.0.1:5001/minar')
print(r.text)

# MOSTRAR LA CADENA DEL NODO 5001 PARA VER
# QUE NO SE HA MINADO UN BLOQUE, SINO QUE
# AHORA TIENE LA CADENA DEL NODO 5000 (LA MÁS
# LARGA DE LA RED)
r = requests.get('http://127.0.0.1:5001/chain')
print(r.text)

# MOTRAR LOS DATOS DEL SISTEMA
r = requests.get('http://127.0.0.1:5001/system')
print(r.text)
