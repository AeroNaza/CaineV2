import speech_recognition as sr

print("Micrófonos detectados:")
for i, nombre in enumerate(sr.Microphone.list_microphone_names()):
    print(i, nombre)

r = sr.Recognizer()
with sr.Microphone() as src:
    print("Calibrando ruido...")
    r.adjust_for_ambient_noise(src, duration=0.5)
    print("Habla ahora, tienes 5 segundos...")
    audio = r.listen(src, timeout=5, phrase_time_limit=4)

print("Capturado, reconociendo...")
try:
    print("Escuchaste:", r.recognize_google(audio, language="es-CO"))
except Exception as e:
    print("Error:", e)
