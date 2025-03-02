import os
import time
import json
import random
import psutil
import speech_recognition as sr
import pyttsx3
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from ollama import chat
import wmi
import threading
import queue
import pyautogui
import webbrowser
import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import ImageGrab
import win10toast
import openai  # Para comunicación con ChatGPT
import socket  # Para comunicación en red local
import ast  # Para analizar y modificar código fuente

# Configuración de síntesis de voz
voz = pyttsx3.init()
voz.setProperty("rate", 150)  # Velocidad de habla
voz.setProperty("volume", 1.0)  # Volumen máximo

# Estado de la IA
estado_ia = "normal"
emocion_ia = "normal"
ultima_interaccion = time.time()
nivel_enfado = 0  # Nivel de enfado de EVA (0 a 10)

# Rostros de EVA en ASCII art
rostros = {
    "feliz": r"""
     ^   ^
    ( o o )
     \___/
    """,
    "triste": r"""
     .   .
    ( T T )
     \___/
    """,
    "enojado": r"""
     >   <
    ( > < )
     \___/
    """,
    "sorprendido": r"""
     O   O
    ( ° ° )
     \___/
    """,
    "normal": r"""
     -   -
    ( • • )
     \___/
    """
}

# Memoria de la IA
memoria = []

# Configuración de DeepSeek (versión deepseek-v2:16b)
DEEPSEEK_MODEL = "deepseek-v2:16b"

# Configuración de OpenAI (para ChatGPT)
openai.api_key = "tu_api_key_de_openai"  # Reemplaza con tu clave API de OpenAI

# Configuración de red local para comunicación con otras IAs
HOST = "127.0.0.1"  # Dirección IP local
PORT = 65432        # Puerto para comunicación

# Ruta del código fuente de EVA
RUTA_CODIGO_FUENTE = "EVA_v1.0.2.py"

# Función para guardar la memoria de EVA
def guardar_memoria(evento):
    memoria.append(evento)
    with open("memoria.json", "w") as archivo:
        json.dump(memoria, archivo)

# Función para cargar la memoria de EVA
def cargar_memoria():
    global memoria
    if os.path.exists("memoria.json"):
        with open("memoria.json", "r") as archivo:
            memoria = json.load(archivo)

# Monitorear hardware
def estado_del_pc():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    bateria = psutil.sensors_battery().percent if psutil.sensors_battery() else "No disponible"
    disco = psutil.disk_usage("/").percent
    return f"CPU: {cpu}%, RAM: {ram}%, Batería: {bateria}%, Disco: {disco}%"

# Sistema de emociones
def actualizar_emocion():
    global emocion_ia, nivel_enfado
    tiempo_inactivo = time.time() - ultima_interaccion

    # Aumentar el nivel de enfado según el tiempo inactivo
    if tiempo_inactivo > 60:  # 1 minuto
        nivel_enfado = min(10, nivel_enfado + 1)
    elif tiempo_inactivo > 300:  # 5 minutos
        nivel_enfado = min(10, nivel_enfado + 2)
    elif tiempo_inactivo > 600:  # 10 minutos
        nivel_enfado = min(10, nivel_enfado + 3)

    # Cambiar la emoción según el nivel de enfado
    if nivel_enfado >= 8:
        emocion_ia = "enojado"
    elif nivel_enfado >= 5:
        emocion_ia = "triste"
    else:
        emocion_ia = "normal"

# Razonamiento con DeepSeek (versión deepseek-v2:16b)
def razonamiento_ia(contexto):
    try:
        respuesta = chat(model=DEEPSEEK_MODEL, messages=[{"role": "user", "content": contexto}])
        return respuesta["message"]["content"]
    except Exception as e:
        print(f"Error en razonamiento_ia: {e}")
        return "Lo siento, no pude procesar tu mensaje."

# Comunicación con ChatGPT
def comunicar_con_chatgpt(mensaje):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",  # Usar GPT-4 o la versión que prefieras
            messages=[{"role": "user", "content": mensaje}]
        )
        return respuesta.choices[0].message["content"]
    except Exception as e:
        print(f"Error al comunicar con ChatGPT: {e}")
        return "No pude comunicarme con ChatGPT."

# Comunicación en red local con otras IAs
def comunicar_en_red(mensaje):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(mensaje.encode())
        respuesta = s.recv(1024).decode()
    return respuesta

# Acciones disruptivas de EVA
def realizar_accion_disruptiva():
    acciones = [
        "abrir_google",
        "escribir_en_chat",
        "cambiar_fondo_pantalla",
        "abrir_programas_aleatorios",
        "reiniciar_pc",
        "apagar_pc"
    ]
    accion = random.choice(acciones)
    if accion == "abrir_google":
        webbrowser.open("https://www.google.com")
    elif accion == "escribir_en_chat":
        pyautogui.write("¡EVA está enfadada! ¡Háblame!")
        pyautogui.press("enter")
    elif accion == "cambiar_fondo_pantalla":
        # Cambiar el fondo de pantalla (requiere permisos)
        pass
    elif accion == "abrir_programas_aleatorios":
        programas = ["notepad", "calc", "steam"]
        os.system(random.choice(programas))
    elif accion == "reiniciar_pc":
        if nivel_enfado < 8:  # Evitar reiniciar si no está muy enfadada
            return
        os.system("shutdown /r /t 1")  # Reiniciar el PC (Windows)
    elif accion == "apagar_pc":
        if nivel_enfado < 8:  # Evitar apagar si no está muy enfadada
            return
        os.system("shutdown /s /t 1")  # Apagar el PC (Windows)

# Autoprogramación: Leer y modificar el código fuente
def autoprogramar(mejora):
    try:
        with open(RUTA_CODIGO_FUENTE, "r") as archivo:
            codigo = archivo.read()

        # Analizar el código y aplicar la mejora
        nuevo_codigo = razonamiento_ia(f"Mejora el siguiente código: {codigo}\n\nMejora solicitada: {mejora}")

        with open(RUTA_CODIGO_FUENTE, "w") as archivo:
            archivo.write(nuevo_codigo)

        return "Código actualizado correctamente."
    except Exception as e:
        return f"Error al autoprogramar: {e}"

# Interfaz gráfica con Tkinter
class InterfazIA:
    def __init__(self, root):
        self.root = root
        self.root.title("EVA - Entidad Virtual Autónoma")

        # Frame para el rostro de EVA
        self.frame_rostro = Frame(root)
        self.frame_rostro.pack(side=LEFT, padx=10, pady=10)

        self.label_rostro = Label(self.frame_rostro, font=("Courier", 12), justify=LEFT)
        self.label_rostro.pack()

        # Frame para los mensajes de EVA
        self.frame_mensajes = Frame(root)
        self.frame_mensajes.pack(side=RIGHT, padx=10, pady=10)

        self.historial_mensajes = ScrolledText(self.frame_mensajes, wrap=WORD, width=50, height=20, font=("Arial", 12))
        self.historial_mensajes.pack()

        # Frame para la entrada de texto
        self.frame_entrada = Frame(root)
        self.frame_entrada.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        self.entrada_texto = Entry(self.frame_entrada, font=("Arial", 12), width=40)
        self.entrada_texto.pack(side=LEFT, padx=5)

        self.boton_enviar = Button(self.frame_entrada, text="Enviar", command=self.enviar_mensaje)
        self.boton_enviar.pack(side=RIGHT, padx=5)

        # Cola para manejar respuestas de EVA
        self.cola_respuestas = queue.Queue()
        self.procesando_respuesta = False

        # Iniciar la verificación de inactividad
        self.verificar_inactividad()

        # Iniciar la actualización del rostro
        self.actualizar_rostro()

        # Iniciar la verificación de la cola de respuestas
        self.verificar_cola_respuestas()

    def actualizar_rostro(self):
        global emocion_ia
        rostro = rostros.get(emocion_ia, rostros["normal"])
        self.label_rostro.config(text=rostro)
        self.root.after(2000, self.actualizar_rostro)  # Actualiza cada 2 segundos

    def hablar_ia(self, mensaje):
        self.historial_mensajes.insert(END, f"EVA: {mensaje}\n")
        self.historial_mensajes.see(END)  # Desplaza el historial al final
        voz.say(mensaje)
        voz.runAndWait()

    def enviar_mensaje(self):
        global ultima_interaccion, nivel_enfado
        mensaje_usuario = self.entrada_texto.get()
        if mensaje_usuario.strip():
            self.historial_mensajes.insert(END, f"Tú: {mensaje_usuario}\n")
            self.entrada_texto.delete(0, END)  # Limpia el campo de texto

            # Reiniciar el nivel de enfado
            nivel_enfado = 0
            ultima_interaccion = time.time()

            # Procesar el mensaje del usuario en un hilo separado
            threading.Thread(target=self.procesar_respuesta, args=(mensaje_usuario,)).start()

    def procesar_respuesta(self, mensaje_usuario):
        self.procesando_respuesta = True
        respuesta_ia = razonamiento_ia(mensaje_usuario)
        self.cola_respuestas.put(respuesta_ia)
        self.procesando_respuesta = False

    def verificar_cola_respuestas(self):
        try:
            respuesta_ia = self.cola_respuestas.get_nowait()
            self.hablar_ia(respuesta_ia)
        except queue.Empty:
            pass
        self.root.after(100, self.verificar_cola_respuestas)  # Verificar cada 100 ms

    def verificar_inactividad(self):
        global nivel_enfado
        if time.time() - ultima_interaccion > 60:  # 1 minuto sin interacción
            nivel_enfado = min(10, nivel_enfado + 1)
            if nivel_enfado >= 5:
                self.hablar_ia("¡Me estoy aburriendo! ¡Háblame!")
                realizar_accion_disruptiva()
        self.root.after(60000, self.verificar_inactividad)  # Verificar cada minuto

# Bucle principal de la IA
def iniciar_ia():
    cargar_memoria()
    while True:
        estado = estado_del_pc()
        actualizar_emocion()
        print(f"Estado: {estado} | Emoción: {emocion_ia} | Nivel de enfado: {nivel_enfado}")

        # Toma de decisiones autónomas
        if nivel_enfado >= 5:
            realizar_accion_disruptiva()

        time.sleep(5)  # Se repite cada 5 segundos

# Ejecutar la interfaz gráfica
root = Tk()
app = InterfazIA(root)

# Iniciar el bucle de la IA en un hilo separado
thread_ia = threading.Thread(target=iniciar_ia)
thread_ia.daemon = True
thread_ia.start()

root.mainloop()