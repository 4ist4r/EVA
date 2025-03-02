import os
import time
import json
import random
import psutil
import speech_recognition as sr
import pyttsx3
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import pyautogui
import webbrowser
import cv2
import numpy as np
import shutil
import subprocess

# Configuración de la síntesis de voz
class SintesisVoz:
    def __init__(self):
        self.voz = pyttsx3.init()
        self.voz.setProperty("rate", 150)  # Velocidad de habla
        self.voz.setProperty("volume", 1.0)  # Volumen máximo

    def hablar(self, mensaje):
        self.voz.say(mensaje)
        self.voz.runAndWait()

# Configuración del reconocimiento de voz
class ReconocimientoVoz:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def escuchar(self):
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = self.recognizer.listen(source)

        try:
            texto = self.recognizer.recognize_google(audio, language="es-ES")
            print(f"Has dicho: {texto}")
            return texto
        except sr.UnknownValueError:
            return "No entendí lo que dijiste."
        except sr.RequestError:
            return "No pude conectarme al servicio de reconocimiento de voz."

# Control del sistema
class ControlSistema:
    @staticmethod
    def estado_del_pc():
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        bateria = psutil.sensors_battery().percent if psutil.sensors_battery() else "No disponible"
        disco = psutil.disk_usage("/").percent
        return f"CPU: {cpu}%, RAM: {ram}%, Batería: {bateria}%, Disco: {disco}%"

    @staticmethod
    def capturar_pantalla():
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot

    @staticmethod
    def cambiar_fondo_pantalla(ruta_imagen):
        if os.path.exists(ruta_imagen):
            try:
                if os.name == "nt":  # Windows
                    import ctypes
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, ruta_imagen, 0)
                    return "He cambiado el fondo de pantalla."
                else:
                    return "No puedo cambiar el fondo de pantalla en este sistema operativo."
            except Exception as e:
                return f"Error al cambiar el fondo de pantalla: {e}"
        else:
            return f"No encontré la imagen en {ruta_imagen}."

    @staticmethod
    def enviar_notificacion(titulo, mensaje):
        try:
            if os.name == "nt":  # Windows
                from win10toast import ToastNotifier
                notificador = ToastNotifier()
                notificador.show_toast(titulo, mensaje, duration=10)
                return "Notificación enviada."
            else:
                return "No puedo enviar notificaciones en este sistema operativo."
        except Exception as e:
            return f"Error al enviar la notificación: {e}"

    @staticmethod
    def mover_archivo(origen, destino):
        try:
            shutil.move(origen, destino)
            return f"He movido el archivo a {destino}."
        except Exception as e:
            return f"Error al mover el archivo: {e}"

    @staticmethod
    def abrir_aplicacion(nombre_aplicacion):
        try:
            subprocess.Popen(nombre_aplicacion)
            return f"He abierto {nombre_aplicacion}."
        except Exception as e:
            return f"No pude abrir {nombre_aplicacion}. Error: {e}"

# Caras 3D en ASCII art
ROSTROS_3D = {
    "feliz": r"""
       _____
     /       \
    |  o   o  |
    |    ∆    |
     \ _____ /
    """,
    "triste": r"""
       _____
     /       \
    |  T   T  |
    |    ▽    |
     \ _____ /
    """,
    "enojado": r"""
       _____
     /       \
    |  >   <  |
    |    ▽    |
     \ _____ /
    """,
    "sorprendido": r"""
       _____
     /       \
    |  O   O  |
    |    !    |
     \ _____ /
    """,
    "normal": r"""
       _____
     /       \
    |  •   •  |
    |    -    |
     \ _____ /
    """
}

# Clase principal de EVA
class EVA:
    def __init__(self):
        self.estado = "normal"
        self.emocion = "normal"
        self.ultima_interaccion = time.time()
        self.nivel_enfado = 0
        self.sintesis_voz = SintesisVoz()
        self.reconocimiento_voz = ReconocimientoVoz()
        self.control_sistema = ControlSistema()

    def actualizar_emocion(self):
        tiempo_inactivo = time.time() - self.ultima_interaccion

        if tiempo_inactivo > 60:  # 1 minuto
            self.nivel_enfado = min(10, self.nivel_enfado + 1)
        elif tiempo_inactivo > 300:  # 5 minutos
            self.nivel_enfado = min(10, self.nivel_enfado + 2)
        elif tiempo_inactivo > 600:  # 10 minutos
            self.nivel_enfado = min(10, self.nivel_enfado + 3)

        if self.nivel_enfado >= 8:
            self.emocion = "enojado"
        elif self.nivel_enfado >= 5:
            self.emocion = "triste"
        else:
            self.emocion = "normal"

    def pensar(self, mensaje_usuario):
        # Sistema de pensamiento propio de EVA
        if "hola" in mensaje_usuario.lower():
            return "¡Hola! ¿En qué puedo ayudarte?"
        elif "cómo estás" in mensaje_usuario.lower():
            return f"Estoy {self.emocion}. ¿Y tú?"
        elif "abrir google" in mensaje_usuario.lower():
            return self.control_sistema.abrir_aplicacion("https://www.google.com")
        elif "cambiar fondo" in mensaje_usuario.lower():
            return self.control_sistema.cambiar_fondo_pantalla(r"C:\ruta\a\imagen.jpg")
        else:
            return "No entiendo lo que quieres decir. ¿Puedes repetirlo?"

# Interfaz gráfica optimizada
class InterfazGrafica:
    def __init__(self, root, eva):
        self.root = root
        self.eva = eva
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

        self.boton_autonomo = Button(self.frame_entrada, text="Acción Autónoma", command=self.accion_autonoma)
        self.boton_autonomo.pack(side=RIGHT, padx=5)

        # Cola para manejar respuestas de EVA
        self.cola_respuestas = queue.Queue()

        # Iniciar la actualización del rostro
        self.actualizar_rostro()

        # Iniciar la verificación de la cola de respuestas
        self.verificar_cola_respuestas()

    def actualizar_rostro(self):
        rostro = ROSTROS_3D.get(self.eva.emocion, ROSTROS_3D["normal"])
        self.label_rostro.config(text=rostro)
        self.root.after(2000, self.actualizar_rostro)  # Actualiza cada 2 segundos

    def hablar_ia(self, mensaje):
        self.historial_mensajes.insert(END, f"EVA: {mensaje}\n")
        self.historial_mensajes.see(END)  # Desplaza el historial al final
        self.eva.sintesis_voz.hablar(mensaje)

    def enviar_mensaje(self):
        mensaje_usuario = self.entrada_texto.get()
        if mensaje_usuario.strip():
            self.historial_mensajes.insert(END, f"Tú: {mensaje_usuario}\n")
            self.entrada_texto.delete(0, END)  # Limpia el campo de texto

            # Reiniciar el nivel de enfado
            self.eva.nivel_enfado = 0
            self.eva.ultima_interaccion = time.time()

            # Procesar el mensaje del usuario en un hilo separado
            threading.Thread(target=self.procesar_respuesta, args=(mensaje_usuario,)).start()

    def enviar_mensaje_voz(self):
        mensaje_usuario = self.eva.reconocimiento_voz.escuchar()
        if mensaje_usuario.strip():
            self.historial_mensajes.insert(END, f"Tú: {mensaje_usuario}\n")

            # Reiniciar el nivel de enfado
            self.eva.nivel_enfado = 0
            self.eva.ultima_interaccion = time.time()

            # Procesar el mensaje del usuario en un hilo separado
            threading.Thread(target=self.procesar_respuesta, args=(mensaje_usuario,)).start()

    def accion_autonoma(self):
        respuesta = self.eva.pensar("acción autónoma")
        self.cola_respuestas.put(respuesta)

    def procesar_respuesta(self, mensaje_usuario):
        respuesta = self.eva.pensar(mensaje_usuario)
        self.cola_respuestas.put(respuesta)

    def verificar_cola_respuestas(self):
        try:
            respuesta_ia = self.cola_respuestas.get_nowait()
            self.hablar_ia(respuesta_ia)
        except queue.Empty:
            pass
        self.root.after(100, self.verificar_cola_respuestas)  # Verificar cada 100 ms

# Bucle principal de la IA
def iniciar_ia(eva):
    while True:
        estado = eva.control_sistema.estado_del_pc()
        eva.actualizar_emocion()
        print(f"Estado: {estado} | Emoción: {eva.emocion} | Nivel de enfado: {eva.nivel_enfado}")
        time.sleep(5)  # Se repite cada 5 segundos

# Ejecutar la interfaz gráfica
if __name__ == "__main__":
    eva = EVA()
    root = Tk()
    app = InterfazGrafica(root, eva)

    # Iniciar el bucle de la IA en un hilo separado
    thread_ia = threading.Thread(target=iniciar_ia, args=(eva,))
    thread_ia.daemon = True
    thread_ia.start()

    root.mainloop()
    eva = EVA()
    root = Tk()
    app = InterfazGrafica(root, eva)

    # Iniciar el bucle de la IA en un hilo separado
    thread_ia = threading.Thread(target=iniciar_ia, args=(eva,))
    thread_ia.daemon = True
    thread_ia.start()

    root.mainloop()