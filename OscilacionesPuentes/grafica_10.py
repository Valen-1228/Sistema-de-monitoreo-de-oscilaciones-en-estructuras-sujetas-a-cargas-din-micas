import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Conectar a SQLite (se asume que la base de datos ya existe y contiene datos)
conexion = sqlite3.connect('datos_oscilaciones.db')

# Crear el cursor
cursor = conexion.cursor()

# Función para extraer los datos de la base de datos
def fetch_data():
    cursor.execute("SELECT fecha_hora, num_pic, pic_max, suma_datos, tm_act, max_der_neg, max_der_pos, integ_acum, rms, maxpicRegis FROM datos_oscilaciones ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    # Extraer los datos en listas
    fechas, num_pic, pic_max, suma_datos, tm_act, max_der_neg, max_der_pos, integ_acum, rms, maxpicRegis = zip(*[
        (datetime.strptime(row[0], "%d %b %Y %H:%M:%S"), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]) 
        for row in rows
    ])
    # Devolver los datos en orden cronológico
    return list(reversed(fechas)), list(reversed(num_pic)), list(reversed(pic_max)), list(reversed(suma_datos)), list(reversed(tm_act)), list(reversed(max_der_neg)), list(reversed(max_der_pos)), list(reversed(integ_acum)), list(reversed(rms)), list(reversed(maxpicRegis))

# Inicializar las figuras y subplots
fig, axs = plt.subplots(3, 3, figsize=(5, 8))  # Matriz de 3x3 para los 9 subplots
fig.suptitle('Evolución de Datos')

# Función de actualización para la animación
def update(frame):
    # Obtener los datos de la base de datos
    fechas, num_pic, pic_max, suma_datos, tm_act, max_der_neg, max_der_pos, integ_acum, rms, maxpicRegis = fetch_data()
    
    # Limpiar y actualizar cada subplot
    axs[0, 0].clear()
    axs[0, 0].plot(fechas, num_pic, color="blue")
    axs[0, 0].set_title('NumPic')
    
    axs[0, 1].clear()
    axs[0, 1].plot(fechas, pic_max, color="green")
    axs[0, 1].set_title('PicMax')
    
    axs[0, 2].clear()
    axs[0, 2].plot(fechas, suma_datos, color="red")
    axs[0, 2].set_title('SumaDatos')
    
    axs[1, 0].clear()
    axs[1, 0].plot(fechas, tm_act, color="purple")
    axs[1, 0].set_title('TmAct')
    
    axs[1, 1].clear()
    axs[1, 1].plot(fechas, max_der_neg, color="orange")
    axs[1, 1].set_title('MaxDerNeg')
    
    axs[1, 2].clear()
    axs[1, 2].plot(fechas, max_der_pos, color="brown")
    axs[1, 2].set_title('MaxDerPos')
    
    axs[2, 0].clear()
    axs[2, 0].plot(fechas, integ_acum, color="pink")
    axs[2, 0].set_title('IntegAcum')
    
    axs[2, 1].clear()
    axs[2, 1].plot(fechas, rms, color="cyan")
    axs[2, 1].set_title('RMS')

    axs[2, 2].clear()
    axs[2, 2].plot(fechas, maxpicRegis, color="black")
    axs[2, 2].set_title('MaxPicRegis')

    # Ajustar etiquetas y formato
    for ax in axs.flat:
        ax.set_xlabel('Fecha y Hora')
        ax.set_ylabel('Valor')
        ax.tick_params(axis='x', rotation=25)

# Ajustar espaciado entre subplots
fig.subplots_adjust(hspace=5, top=9)  # Ajustar hspace y top

# Configurar la animación
ani = FuncAnimation(fig, update, interval=1000)  # Intervalo de actualización de 1 segundo

plt.tight_layout()

# Ajustar espaciado entre subplots
fig.subplots_adjust(hspace=1, top=0.9)  # Ajustar hspace y top

plt.show()

# Cerrar la conexión al finalizar
conexion.close()