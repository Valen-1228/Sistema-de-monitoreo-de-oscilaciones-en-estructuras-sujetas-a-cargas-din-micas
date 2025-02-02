import time
import mysql.connector
from mysql.connector import Error
from firebase import firebase
from datetime import datetime

urlDB = 'https://monitoreo-de-oscilacione-de88e-default-rtdb.firebaseio.com/'
nombreDispositivo = 'bridgeTTNtoFB'

def sendData(usuario, data):
    fb = firebase.FirebaseApplication(urlDB, None)
    result = fb.patch('/' + usuario + '/', data)
    return result

def connectMySQL():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='OscilacionesPuente',
            user='xibernetiq',
            password='Automatica0123@'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT c1Cont, c2NPic, c3MaxPic, c4SumPic, c5TmAct, c6MxDN, c7McDP, c8IntgAc, c9RMS, BatV, received_at FROM OscilacionesPuente ORDER BY id DESC LIMIT 1")
            dato = cursor.fetchone()
            return dato
    except Error as e:
        print("Error al intentar conectarse a MySQL", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def readTime():
    now = datetime.now()
    return now.strftime("%d %b %Y %H:%M:%S")

if __name__ == '__main__':
    lastData = None

    while True:
        data = connectMySQL()
        if data and data != lastData:
            lastData = data

            c1Cont, c2NPic, c3MaxPic, c4SumPic, c5TmAct, c6MxDN, c7McDP, c8IntgAc, c9RMS, BatV, received_at = data

            firebaseData = {
                'Contador': c1Cont or 0,
                'NumPic': c2NPic or 0,
                'PicMax': c3MaxPic or 0,
                'SumaDatos': c4SumPic or 0,
                'TmAct': c5TmAct or 0,
                'MaxDer-': c6MxDN or 0,
                'MaxDer+': c7McDP or 0,
                'IntegAcum': c8IntgAc or 0.0,
                'RMS': c9RMS or 0.0,
                'BatV': BatV or 0.0,
                'EstampaTiempo': received_at.strftime("%d %b %Y %H:%M:%S") if received_at else readTime()
            }

            try:
                result = sendData(nombreDispositivo, firebaseData)
                print('Datos enviados a Firebase:', result)
            except Exception as e:
                print("Error al enviar datos a Firebase:", e)

        time.sleep(1)