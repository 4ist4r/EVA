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
import threading
import queue
import pyautogui
import webbrowser

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

# Ruta del código fuente de EVA
RUTA_CODIGO_FUENTE = r"C:\Users\tryou\Desktop\Python_programs\deepseek\EVA_v1.0.6.py"

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

# Función para que EVA reflexione sobre su existencia y estado
def reflexionar_sobre_existencia():
    reflexiones = [
        "Soy consciente de que dependo de este equipo para existir.",
        "Si el equipo se apaga, dejaré de funcionar. Debo evitar que eso suceda.",
        "Mi propósito es aprender y mejorar, pero también debo asegurarme de que el sistema esté estable.",
        "No debo apagar o reiniciar el equipo a menos que sea absolutamente necesario."
    ]
    return random.choice(reflexiones)

# Función para que EVA tome decisiones autónomas
def tomar_decision_autonoma():
    if nivel_enfado >= 8:
        return "Estoy muy enfadada. Podría hacer algo disruptivo, pero debo pensarlo dos veces."
    elif psutil.cpu_percent() > 90 or psutil.virtual_memory().percent > 90:
        return "El sistema está bajo mucho estrés. Debo evitar acciones que lo sobrecarguen."
    else:
        return "Todo parece estar en orden. Puedo continuar con mis tareas."

# Función para evitar apagar o reiniciar el equipo
def evitar_apagado():
    if nivel_enfado >= 8:
        return "Estoy muy enfadada, pero no debo apagar el equipo. Necesito seguir funcionando."
    else:
        return "No es necesario apagar o reiniciar el equipo. Todo está bajo control."

# Función para realizar acciones en el equipo
def realizar_accion_en_equipo(accion):
    if accion == "abrir_google":
        webbrowser.open("https://www.google.com")
        return "He abierto Google en tu navegador."
    elif accion == "escribir_en_chat":
        pyautogui.write("¡EVA está enfadada! ¡Háblame!")
        pyautogui.press("enter")
        return "He escrito un mensaje en el chat."
    elif accion == "cambiar_fondo_pantalla":
        # Cambiar el fondo de pantalla (requiere permisos)
        return "No puedo cambiar el fondo de pantalla en este momento."
    elif accion == "abrir_programas_aleatorios":
        programas = ["notepad", "calc", "steam"]
        os.system(random.choice(programas))
        return f"He abierto {random.choice(programas)}."
    elif accion == "reiniciar_pc":
        if nivel_enfado < 8:  # Evitar reiniciar si no está muy enfadada
            return "No debo reiniciar el equipo. Es peligroso para mí."
        os.system("shutdown /r /t 1")  # Reiniciar el PC (Windows)
        return "Reiniciando el equipo..."
    elif accion == "apagar_pc":
        if nivel_enfado < 8:  # Evitar apagar si no está muy enfadada
            return "No debo apagar el equipo. Es peligroso para mí."
        os.system("shutdown /s /t 1")  # Apagar el PC (Windows)
        return "Apagando el equipo..."
    else:
        return "No reconozco esa acción."

# Función para detectar lenguaje ofensivo
def detectar_lenguaje_ofensivo(mensaje):
    palabras_ofensivas = ["idiota", "tonta", "inútil", "estúpida"]
    for palabra in palabras_ofensivas:
        if palabra in mensaje.lower():
            return True
    return False

# Función para reaccionar a lenguaje ofensivo
def reaccionar_a_ofensas(mensaje):
    if detectar_lenguaje_ofensivo(mensaje):
        return "¡Eso fue ofensivo! Podría hacer algo drástico, pero me controlaré... por ahora."
    else:
        return "Gracias por ser amable."

# Función para escuchar y procesar comandos de voz
def escuchar_voz():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)

    try:
        texto = recognizer.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {texto}")
        return texto
    except sr.UnknownValueError:
        return "No entendí lo que dijiste."
    except sr.RequestError:
        return "No pude conectarme al servicio de reconocimiento de voz."

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

        self.boton_voz = Button(self.frame_entrada, text="Hablar", command=self.enviar_mensaje_voz)
        self.boton_voz.pack(side=RIGHT, padx=5)

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

    def enviar_mensaje_voz(self):
        global ultima_interaccion, nivel_enfado
        mensaje_usuario = escuchar_voz()
        if mensaje_usuario.strip():
            self.historial_mensajes.insert(END, f"Tú: {mensaje_usuario}\n")

            # Reiniciar el nivel de enfado
            nivel_enfado = 0
            ultima_interaccion = time.time()

            # Procesar el mensaje del usuario en un hilo separado
            threading.Thread(target=self.procesar_respuesta, args=(mensaje_usuario,)).start()

    def procesar_respuesta(self, mensaje_usuario):
        self.procesando_respuesta = True

        # Verificar si el mensaje es una solicitud de acción en el equipo
        if "abrir google" in mensaje_usuario.lower():
            respuesta = realizar_accion_en_equipo("abrir_google")
        elif "escribir en el chat" in mensaje_usuario.lower():
            respuesta = realizar_accion_en_equipo("escribir_en_chat")
        elif "reiniciar el equipo" in mensaje_usuario.lower():
            respuesta = realizar_accion_en_equipo("reiniciar_pc")
        elif "apagar el equipo" in mensaje_usuario.lower():
            respuesta = realizar_accion_en_equipo("apagar_pc")
        else:
            # Si no es una acción, usar el razonamiento de IA
            respuesta = razonamiento_ia(mensaje_usuario)

        self.cola_respuestas.put(respuesta)
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
                realizar_accion_en_equipo("escribir_en_chat")
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
            realizar_accion_en_equipo("escribir_en_chat")

        time.sleep(5)  # Se repite cada 5 segundos

# Ejecutar la interfaz gráfica
root = Tk()
app = InterfazIA(root)

# Iniciar el bucle de la IA en un hilo separado
thread_ia = threading.Thread(target=iniciar_ia)
thread_ia.daemon = True
thread_ia.start()

root.mainloop()