from __future__ import division
import time
from firebase import firebase
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sqlite3

# Conectar a SQLite (o crear la base de datos si no existe)
conexion = sqlite3.connect('datos_oscilaciones.db')

# Crear un cursor
cursor = conexion.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos_oscilaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora TEXT NOT NULL,
        num_pic INTEGER,
        pic_max INTEGER,
        suma_datos INTEGER,
        tm_act INTEGER,
        max_der_neg INTEGER,
        max_der_pos INTEGER,
        integ_acum INTEGER,
        rms INTEGER,
        maxpicRegis INTEGER
               
    )
''')

# Guardar cambios
conexion.commit()

#link de Firebase Realtime
urlDB = 'https://monitoreo-de-oscilacione-de88e-default-rtdb.firebaseio.com/'

# Firebase
def sendData(usuario, var1, var2, tiempo):
    data = {'Dato1': var1, 'Dato2': var2, 'EstampaTiempo': tiempo}
    fb = firebase.FirebaseApplication(urlDB, None)
    result = fb.patch('/' + usuario + '/', data)
    return result

def getData(usuario):
    fb = firebase.FirebaseApplication(urlDB, None)
    result = fb.get('/' + usuario + '/', None)
    return result

#tiempo
def readTime(tipo):
    timeStamp = time.strftime("%d %b %Y %H:%M:%S", time.localtime())
    if tipo == 0:
        now = datetime.now()
        timeStamp = datetime.timestamp(now)
    return timeStamp

# Declarar variables globales
NumPic = PicMax = SumaDatos = TmAct = MaxDerNeg = MaxDerPos = IntegAcum = RMS = maxpicRegis = 0

#Pide los datos del servidor
def update_data():
    global NumPic, PicMax, SumaDatos, TmAct, MaxDerNeg, MaxDerPos, IntegAcum, RMS, maxpicRegis
    # Obtener todos los datos de Firebase
    oscilaciones_data = getData('bridgeTTNtoFB')

    # Asignar los valores, utilizando 0 si no existen
    NumPic = int(oscilaciones_data.get('NumPic', 0))
    PicMax = int(oscilaciones_data.get('PicMax', 0))
    SumaDatos = int(oscilaciones_data.get('SumaDatos', 0))
    TmAct = int(oscilaciones_data.get('TmAct', 0))
    MaxDerNeg = int(oscilaciones_data.get('MaxDer-', 0))
    MaxDerPos = int(oscilaciones_data.get('MaxDer+', 0))
    IntegAcum = int(oscilaciones_data.get('IntegAcum', 0))
    RMS = int(oscilaciones_data.get('RMS', 0))

    maxpicRegis = int((getData('PicMaxRegis')).get('Dato1', 0))

update_data()  # Llamar para obtener los datos al inicio

#Guarda los datos de manera local SQLite
def saveData():
    # Insertar los datos en la base de datos SQLite
    cursor.execute('''
        INSERT INTO datos_oscilaciones 
        (fecha_hora, num_pic, pic_max, suma_datos, tm_act, max_der_neg, max_der_pos, integ_acum, rms, maxpicRegis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (readTime(1), NumPic, PicMax, SumaDatos, TmAct, MaxDerNeg, MaxDerPos, IntegAcum, RMS, maxpicRegis))

    # Guardar cambios en la base de datos
    conexion.commit()
    print("Guardado en SQLite")

# Programa principal
if __name__ == "__main__":
    contadorMaxPic = 0
    oldData = 0
    StadoCarga = 0

    maxpicRegisOld = maxpicRegis

    while True:
        newData = int(getData('bridgeTTNtoFB').get('Contador'))
        if newData < oldData:
            print("\nRESET Sensor")
            oldData = 0
            maxpicRegisOld = 0
            contadorMaxPic = 0
            StadoCarga = 0

        if newData > oldData:
            oldData = newData
            StadoCarga = 0

            print("\nRecepción de datos desde Firebase")

            # Llamar a update_data() para obtener datos actualizados
            update_data()

            if PicMax > maxpicRegisOld:
                maxpicRegisOld = PicMax
                contadorMaxPic += 1
                RegisMaxPic = sendData('PicMaxRegis', maxpicRegisOld, contadorMaxPic, readTime(1))
                print('Pico máximos registrado y enviado:', RegisMaxPic)

            DowMaxPic = int((getData('PicMaxRegis')).get('Dato1'))
            print('Pico maximo:', DowMaxPic)
            
            #Guarda los datos en SQLite
            saveData()

        if newData == oldData and StadoCarga == 0:
            print("Esperando Datos")
            StadoCarga = 1
        
        time.sleep(1)  # delay de 1 segundo
