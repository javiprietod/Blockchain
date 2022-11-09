import json
import datetime


def copia_seguridad():
    copia = f'respaldo-nodo-.json'
    while True:
        response ={
            'longitud': 2,
            'date': datetime.date.today()
            }
        with open(copia, 'a') as file:
            #mutex.acquire()
            #file.write("a")
            json.dump(response,file, default=str,indent=1)
            #mutex.release()
            file.close()
if __name__ == '__main__':
    copia_seguridad()