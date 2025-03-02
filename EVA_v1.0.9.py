import os
import time
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import pyttsx3
import speech_recognition as sr
import psutil

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

# Base de datos para almacenar interacciones
class BaseDeDatos:
    def __init__(self, archivo_db="eva.db"):
        self.archivo_db = archivo_db
        self.conexion = sqlite3.connect(self.archivo_db)
        self.crear_tabla()

    def crear_tabla(self):
        cursor = self.conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pregunta TEXT,
                respuesta TEXT,
                contexto TEXT
            )
        """)
        self.conexion.commit()

    def guardar_interaccion(self, pregunta, respuesta, contexto=""):
        cursor = self.conexion.cursor()
        cursor.execute("""
            INSERT INTO interacciones (pregunta, respuesta, contexto)
            VALUES (?, ?, ?)
        """, (pregunta, respuesta, contexto))
        self.conexion.commit()

    def obtener_interacciones(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT pregunta, respuesta FROM interacciones")
        return cursor.fetchall()

# Sistema de aprendizaje de EVA
class AprendizajeEVA:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.base_de_datos = BaseDeDatos()
        self.entrenar_modelo()

    def entrenar_modelo(self):
        interacciones = self.base_de_datos.obtener_interacciones()
        if interacciones:
            preguntas = [pregunta for pregunta, _ in interacciones]
            self.vectorizer.fit(preguntas)

    def predecir_respuesta(self, pregunta):
        interacciones = self.base_de_datos.obtener_interacciones()
        if not interacciones:
            return "No sé cómo responder a eso. ¿Puedes enseñarme?"

        preguntas = [pregunta for pregunta, _ in interacciones]
        respuestas = [respuesta for _, respuesta in interacciones]

        # Vectorizar la pregunta nueva
        pregunta_vector = self.vectorizer.transform([pregunta])

        # Calcular similitud con preguntas existentes
        similitudes = cosine_similarity(pregunta_vector, self.vectorizer.transform(preguntas))
        indice_max_similitud = similitudes.argmax()

        if similitudes[0][indice_max_similitud] > 0.6:  # Umbral de similitud
            return respuestas[indice_max_similitud]
        else:
            return "No sé cómo responder a eso. ¿Puedes enseñarme?"

    def aprender(self, pregunta, respuesta):
        self.base_de_datos.guardar_interaccion(pregunta, respuesta)
        self.entrenar_modelo()

# Clase principal de EVA
class EVA:
    def __init__(self):
        self.estado = "normal"
        self.emocion = "normal"
        self.ultima_interaccion = time.time()
        self.nivel_enfado = 0
        self.sintesis_voz = SintesisVoz()
        self.reconocimiento_voz = ReconocimientoVoz()
        self.aprendizaje = AprendizajeEVA()
        self.iq = 100  # IQ inicial
        self.entrenamiento_activo = True  # Entrenamiento activo por defecto

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
        if self.entrenamiento_activo:
            respuesta = self.aprendizaje.predecir_respuesta(mensaje_usuario)
            if "No sé cómo responder" in respuesta:
                # Si no sabe, pide ayuda al usuario
                self.sintesis_voz.hablar(respuesta)
                respuesta_usuario = self.reconocimiento_voz.escuchar()
                if respuesta_usuario.strip():
                    self.aprendizaje.aprender(mensaje_usuario, respuesta_usuario)
                    self.iq += 1  # Aumentar IQ al aprender algo nuevo
                    return f"Gracias por enseñarme. Ahora sé que '{mensaje_usuario}' se responde con '{respuesta_usuario}'."
            return respuesta
        else:
            return "El entrenamiento está desactivado. No puedo aprender de esta interacción."

    def monitorear_equipo(self):
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            print(f"Monitoreo: CPU {cpu}%, RAM {ram}%")
            time.sleep(10)  # Monitorear cada 10 segundos

# Interfaz gráfica optimizada
# Caras 3D en ASCII art (definidas al principio del archivo)
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

# Clase InterfazGrafica
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

        # Cola para manejar respuestas de EVA
        self.cola_respuestas = queue.Queue()

        # Iniciar la actualización del rostro
        self.actualizar_rostro()

        # Iniciar la verificación de la cola de respuestas
        self.verificar_cola_respuestas()

    def actualizar_rostro(self):
        rostro = ROSTROS_3D.get(self.eva.emocion, ROSTROS_3D["normal"])  # Acceso a ROSTROS_3D
        self.label_rostro.config(text=rostro)
        self.root.after(2000, self.actualizar_rostro)  # Actualiza cada 2 segundos

    # Resto del código...
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

        self.boton_entrenamiento = Button(self.frame_entrada, text="Desactivar Entrenamiento", command=self.toggle_entrenamiento)
        self.boton_entrenamiento.pack(side=RIGHT, padx=5)

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

    def toggle_entrenamiento(self):
        self.eva.entrenamiento_activo = not self.eva.entrenamiento_activo
        estado = "Activado" if self.eva.entrenamiento_activo else "Desactivado"
        self.boton_entrenamiento.config(text=f"{estado} Entrenamiento")
        self.hablar_ia(f"Entrenamiento {estado.lower()}.")

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
        eva.actualizar_emocion()
        print(f"Estado: {eva.estado} | Emoción: {eva.emocion} | Nivel de enfado: {eva.nivel_enfado} | IQ: {eva.iq}")
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

    # Iniciar el monitoreo del equipo en un hilo separado
    thread_monitoreo = threading.Thread(target=eva.monitorear_equipo)
    thread_monitoreo.daemon = True
    thread_monitoreo.start()

    root.mainloop()