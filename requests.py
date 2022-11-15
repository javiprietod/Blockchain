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