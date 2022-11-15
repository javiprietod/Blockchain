import requests
import json
# Cabecera JSON (comun a todas)
cabecera ={'Content-type': 'application/json', 'Accept': 'text/plain'}
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r =requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
r =requests.get('http://127.0.0.1:5000/minar')
print(r.text)
r =requests.get('http://127.0.0.1:5000/chain')
print(r.text)

nodos_a_registrar = {
	"direccion_nodos": ['http://127.0.0.1:5001', 'http://127.0.0.1:5002']
}

r = requests.post('http://127.0.0.1:5000/nodos/registrar', data =json.dumps(nodos_a_registrar), headers=cabecera)
print(r.text)

transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r =requests.post('http://127.0.0.1:5000/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
r =requests.get('http://127.0.0.1:5000/minar')
print(r.text)

transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}
r =requests.post('http://127.0.0.1:5001/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.text)
r =requests.get('http://127.0.0.1:5001/chain')
print(r.text)
r =requests.get('http://127.0.0.1:5001/minar')
print(r.text)
r =requests.get('http://127.0.0.1:5001/chain')
print(r.text)

r =requests.get('http://127.0.0.1:5001/system')
print(r.text)