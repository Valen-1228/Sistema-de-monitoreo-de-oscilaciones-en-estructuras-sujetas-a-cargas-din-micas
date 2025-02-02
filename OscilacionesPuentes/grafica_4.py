import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Conectar a SQLite
conexion = sqlite3.connect('datos_oscilaciones.db')
cursor = conexion.cursor()

# Función para extraer los datos de NumPic
def fetch_data():
    cursor.execute("SELECT fecha_hora, tm_act FROM datos_oscilaciones ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    fechas, tm_act = zip(*[
        (datetime.strptime(row[0], "%d %b %Y %H:%M:%S"), row[1])
        for row in rows
    ])
    return list(reversed(fechas)), list(reversed(tm_act))

# Crear la gráfica
fig, ax = plt.subplots()

# Función de actualización
def update(frame):
    fechas, tm_act = fetch_data()
    ax.clear()
    ax.plot(fechas, tm_act, color="blue")
    ax.set_title('Pico máximo encontrado')
    ax.set_xlabel('Fecha y Hora')
    ax.set_ylabel('Valor')
    ax.tick_params(axis='x', rotation=45)

# Animación
ani = FuncAnimation(fig, update, interval=1000)
plt.tight_layout()
plt.show()

# Cerrar la conexión
conexion.close()
