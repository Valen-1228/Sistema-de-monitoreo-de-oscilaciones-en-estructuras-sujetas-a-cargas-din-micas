import tkinter as tk
from PIL import Image, ImageTk
import subprocess

# Diccionario para guardar los procesos abiertos
process_dict = {}

def open_script(button_id):
    global process_dict
    
    # Si el proceso ya está corriendo, no abrirlo de nuevo
    if button_id in process_dict and process_dict[button_id].poll() is None:
        return
    
    # Genera el nombre del script según el botón
    script_path = f"grafica_{button_id}.py"
    
    # Abre el script con un nuevo proceso
    process_dict[button_id] = subprocess.Popen(["python3", script_path])

def close_script(button_id):
    global process_dict
    if button_id in process_dict and process_dict[button_id].poll() is None:
        # Cierra el proceso si está corriendo
        process_dict[button_id].terminate()

def on_closing():
    # Cierra todos los procesos abiertos al cerrar la ventana principal
    for button_id, process in process_dict.items():
        if process.poll() is None:
            process.terminate()
    root.destroy()

# Crear ventana principal
root = tk.Tk()
root.title("Control de Gráficas")
root.geometry("1080x1920")  # Tamaño inicial
root.configure(bg="#dfe6e9")  # Color de fondo de la ventana principal

# **TÍTULO PRINCIPAL**
title_label = tk.Label(root, text="Control de Gráficas", font=("Helvetica", 18, "bold"), bg="#dfe6e9", fg="#2d3436")
title_label.pack(pady=10)

# **MARCO PARA LOS BOTONES**
button_frame = tk.Frame(root, bg="#dfe6e9")  # Fondo del marco de botones
button_frame.pack(pady=20, padx=20)

# **LISTA DE BOTONES CON INFORMACIÓN**
buttons_info = [
    ("Número de Picos  ", "Muestra la gráfica de número de picos detectados.", 1),
    ("Picos Máximos  ", "Muestra la gráfica de el valor máximo detectado.", 2),
    ("Suma de Datos  ", "Muestra la suma de los datos registrados.", 3),
    ("Tiempo de Actividad  ", "Indica el tiempo en actividad registrado.", 4),
    ("Máxima Derivada Negativa  ", "Muestra el valor de la máxima derivada negativa.", 5),
    ("Máxima Derivada Positiva  ", "Muestra el valor de la máxima derivada positiva.", 6),
    ("Integral Acumulada  ", "Muestra la integral acumulada de los datos registrados.", 7),
    ("RMS  ", "Registra el valor cuadrático medio (RMS). de los datos registrados", 8),
    ("Registro Máximo de Picos  ", "Visualiza los registros de picos máximos detectados a lo largo del tiempo (máximo de 50 valores).", 9),
    ("Gráficas Conjuntas  ", "Visualiza todas las gráficas juntas mediante subplots.", 10)
]

# **FUNCIONES PARA MOSTRAR AYUDA**
def show_help(event, message):
    help_label.config(text=message)

def hide_help(event):
    help_label.config(text="")

# **ETIQUETA PARA MOSTRAR AYUDA**
help_label = tk.Label(root, text="", font=("Arial", 12), bg="#dfe6e9", fg="#1c699d", wraplength=400)
help_label.pack(pady=10)

# **CREAR LOS BOTONES CON AYUDA**
button_width = 25  # Ancho del botón (puedes ajustarlo según sea necesario)
button_height = 1  # Alto del botón (puedes ajustarlo según sea necesario)

for i, (btn_text, tooltip_text, button_id) in enumerate(buttons_info):
    # Ícono
    try:
        icon_path = "nextF.png"  # Asegúrate de que el archivo esté en esta ruta
        icon = Image.open(icon_path).resize((24, 24))  # Asegúrate de que los íconos existen en el directorio
        icon_photo = ImageTk.PhotoImage(icon)
    except FileNotFoundError:
        icon_photo = None  # Usa None si no se encuentra el ícono

    # Crear el botón con estilo
    button = tk.Button(
        button_frame, text=btn_text, image=None, compound="right",
        font=("Arial", 12), bg="#ffffff", fg="#050505", relief="raised",
        width=button_width, height=button_height,  # Ajusta el tamaño aquí
        command=lambda b=button_id: open_script(b)
    )
    
    button.grid(row=i, column=0, padx=10, pady=10, sticky="w")
    button.image = icon_photo  # Evita que Python recolecte el ícono como basura

    # Crear un Frame interno para el ícono a la derecha
    frame = tk.Frame(button_frame, bg="#dfe6e9")
    frame.grid(row=i, column=1, padx=10, pady=10, sticky="e")

    icon_label = tk.Label(frame, image=icon_photo, bg="#dfe6e9")
    icon_label.pack(side="right")  # Alinea el ícono a la derecha del Frame

    # Crear el icono de ayuda junto al botón
    help_icon = tk.Label(button_frame, text="❓", font=("Arial", 14), fg="#1c699d", bg="#dfe6e9")
    help_icon.grid(row=i, column=2, padx=10, pady=10, sticky="w")
    
    # Asignar eventos para mostrar y ocultar la ayuda
    help_icon.bind("<Enter>", lambda e, msg=tooltip_text: show_help(e, msg))
    help_icon.bind("<Leave>", hide_help)

# **CERRAR TODOS LOS SCRIPTS AL CERRAR LA VENTANA PRINCIPAL**
root.protocol("WM_DELETE_WINDOW", on_closing)

# **EJECUTAR SCRIPT ADICIONAL SI LO NECESITAS**
subprocess.Popen(["python3", "RecepcionToDBSQLite.py"])
subprocess.Popen(["python3", "Envio_Firebase.py"])

# **EJECUTAR LA VENTANA PRINCIPAL**
root.mainloop()
