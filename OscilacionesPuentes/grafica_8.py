import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Conectar a SQLite
conexion = sqlite3.connect('datos_oscilaciones.db')
cursor = conexion.cursor()

# Función para extraer los datos de NumPic
def fetch_data():
    cursor.execute("SELECT fecha_hora, rms FROM datos_oscilaciones ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    fechas, rms = zip(*[
        (datetime.strptime(row[0], "%d %b %Y %H:%M:%S"), row[1])
        for row in rows
    ])
    return list(reversed(fechas)), list(reversed(rms))

# Crear la gráfica
fig, ax = plt.subplots()

# Función de actualización
def update(frame):
    fechas, rms = fetch_data()
    ax.clear()
    ax.plot(fechas, rms, color="blue")
    ax.set_title('Raiz cuadrática media')
    ax.set_xlabel('Fecha y Hora')
    ax.set_ylabel('Valor')
    ax.tick_params(axis='x', rotation=45)

# Animación
ani = FuncAnimation(fig, update, interval=1000)
plt.tight_layout()
plt.show()

# Cerrar la conexión
conexion.close()
