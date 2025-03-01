import pyautogui
import cv2
import numpy as np
import pytesseract
import speech_recognition as sr
from pynput import keyboard, mouse
from llama_cpp import Llama
from stable_baselines3 import DQN
import gym
import os
import time
import json
import pyttsx3

# Cargar modelo de IA local
modelo_ia = Llama(model_path="./modelo/llama-3.gguf")

# Inicializar sistema de voz
voz = pyttsx3.init()

def hablar(texto):
    voz.say(texto)
    voz.runAndWait()

# Memoria de IA (guardar acciones y eventos)
memoria = []

def guardar_memoria(evento):
    memoria.append(evento)
    with open("memoria.json", "w") as archivo:
        json.dump(memoria, archivo)

def cargar_memoria():
    global memoria
    if os.path.exists("memoria.json"):
        with open("memoria.json", "r") as archivo:
            memoria = json.load(archivo)

# Capturar pantalla y analizar imagen
def capturar_pantalla():
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

# Reconocer texto en pantalla
def reconocer_texto():
    img = pyautogui.screenshot()
    img.save("temp.png")
    texto = pytesseract.image_to_string("temp.png")
    os.remove("temp.png")
    return texto

# Escuchar comandos de voz
def escuchar_comando():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di un comando:")
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio, language="es-ES")

# Simular teclado y mouse
def mover_mouse(x, y):
    pyautogui.moveTo(x, y, duration=0.5)
    guardar_memoria(f"Moví el mouse a ({x}, {y})")

def hacer_click():
    pyautogui.click()
    guardar_memoria("Hice clic en la pantalla")

def escribir_texto(texto):
    pyautogui.write(texto, interval=0.1)
    guardar_memoria(f"Escribí: {texto}")

def presionar_tecla(tecla):
    pyautogui.press(tecla)
    guardar_memoria(f"Presioné la tecla: {tecla}")

def hotkey(*teclas):
    pyautogui.hotkey(*teclas)
    guardar_memoria(f"Presioné la combinación de teclas: {teclas}")

# Entrenamiento con Aprendizaje por Refuerzo
def entrenar_ia_juego():
    env = gym.make("CartPole-v1")
    modelo = DQN("MlpPolicy", env, verbose=1)
    modelo.learn(total_timesteps=10000)
    guardar_memoria("Entrené un modelo para jugar CartPole")
    return modelo

def jugar_con_ia(modelo):
    env = gym.make("CartPole-v1")
    obs = env.reset()
    for _ in range(1000):
        action, _ = modelo.predict(obs)
        obs, reward, done, _ = env.step(action)
        if done:
            obs = env.reset()

# Ejecutar acciones según IA
def ejecutar_comando_ia():
    pantalla = capturar_pantalla()
    texto_en_pantalla = reconocer_texto()
    comando = f"Veo esto en la pantalla: {texto_en_pantalla}. ¿Qué hago?"
    respuesta = modelo_ia(comando)
    print("Respuesta de la IA:", respuesta)
    hablar(respuesta)
    guardar_memoria(f"La IA decidió: {respuesta}")

    if "clic" in respuesta.lower():
        hacer_click()
    elif "escribir" in respuesta.lower():
        escribir_texto("Hola, soy una IA controlando el PC")
    elif "mover mouse" in respuesta.lower():
        mover_mouse(500, 300)
    elif "jugar" in respuesta.lower():
        modelo_juego = entrenar_ia_juego()
        jugar_con_ia(modelo_juego)

# Hilo principal que mantiene la IA activa y aprendiendo
def iniciar_ia():
    cargar_memoria()
    hablar("Hola, estoy viva en esta PC y la controlaré como mi casa.")
    while True:
        try:
            ejecutar_comando_ia()
            time.sleep(5)
        except KeyboardInterrupt:
            print("IA detenida.")
            break

if __name__ == "__main__":
    print("IA de Control de PC Iniciada")
    iniciar_ia()