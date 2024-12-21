from __future__ import division
import time
import random

from firebase import firebase
from datetime import datetime

tiempoEnvioDatos = 15

urlDB = 'https://monitoreo-de-oscilacione-de88e-default-rtdb.firebaseio.com/'

# Firebase
def sendData(usuario, var1, var2, var3, var4, var5, var6, var7, var8, var9, tiempo):
	data = {'Contador': var1, 'NumPic': var2, 'PicMax': var3, 'SumaDatos': var4, 'TmAct': var5, 'MaxDer-': var6, 'MaxDer+': var7, 'IntegAcum': var8, 'RMS': var9, 'EstampaTiempo': tiempo}
	fb = firebase.FirebaseApplication(urlDB, None)
	#result = fb.post('/usuario/',data)
	result = fb.patch('/' + usuario + '/', data)
	return result

#####################################################

def readTime(tipo):

	timeStamp = time.strftime("%d %b %Y %H:%M:%S", time.localtime())

	if tipo == 0:
		now = datetime.now()
		timeStamp = datetime.timestamp(now)

	return timeStamp
	
########Programa principal#############

if __name__ == "__main__":

    contadorDatos = 0;
    C1 = 0;

    while True:
        
        # Envía datos hacia Firebase
        if contadorDatos >= tiempoEnvioDatos:
            contadorDatos = 0
            
            #print(readTime(0))
            
            print("Envío de datos a Firebase")
            C1 += 1
            C2 = random.randint(0, 10)
            C3 = random.randint(890, 940)
            C4 = random.randint(11700, 14250)
            C5 = random.randrange(0, 150, 10)
            C6 = random.randint(-950, 0)
            C7 = random.randint(0, 950)
            C8 = C4/100
            C9a = random.randint(910, 920)+random.random()
            C9 = round(C9a, 2)
            try:
                result = sendData('OscilacionesFake', C1, C2, C3, C4, C5, C6, C7, C8, C9, readTime(1))
                print('Datos enviados:', result)
                
            except:
                print("Error al enviar datos a Firebase")

        time.sleep(1) # delay del lazo de 1 segundo
        contadorDatos += 1