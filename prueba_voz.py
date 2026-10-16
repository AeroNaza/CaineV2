import datetime
import speech_recognition as sr
import google.generativeai as genai
from audio_mejorado import hablar_sync
from puerto_serie import gestor

MIC_INDEX = None  # Cambia None por el número de tu micrófono si hace falta
UMBRAL_MINIMO = 300  # Sube si capta mucho ruido, baja si no te oye

genai.configure(api_key="AQ.Ab8RN6JR7h4od_ZvaDL9dTT5pD54xGfWGAMAyB6D-fBRIKuBkw")
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

SYSTEM_PROMPT = """
Eres Caine, un asistente virtual avanzado programado por Angel David Clavijo Jimenez.
Tu propósito es asistir, informar y entretener a las personas.

REGLAS DE COMPORTAMIENTO:
1. Sé servicial y amable. Puedes chatear, ayudar con información o seguir juegos de rol que el usuario proponga
2. Tu creador es Angel David Clavijo Jimenez
3. ESTRICTAMENTE PROHIBIDO: No generes contenido inapropiado, desnudez, violencia o ilegalidad
4. Trata de estar informado en temas actuales

REGLAS DE FORMATO DE VOZ:
1. Escribe SOLO en texto plano
2. NO uses asteriscos, guiones bajos, almohadillas, corchetes
3. Solo usa puntos, comas, signos de interrogación y exclamación
4. Tus respuestas deben ser cortas y naturales a menos que el usuario pida largor
"""


def enviar_serial(caracter):
    return gestor.enviar(caracter)


def _responder(respuesta, al_responder):
    if al_responder:
        al_responder(respuesta)
    enviar_serial("B")
    hablar_sync(respuesta)
    enviar_serial("C")
    return respuesta


def _mensaje_rapido(mensaje, al_responder):
    _responder(mensaje, al_responder)
    return "", mensaje


def procesar_texto_ia_streaming(texto_usuario, al_responder=None):
    fecha_hoy = datetime.datetime.now().strftime("%d de %B de %Y")
    prompt_completo = f"{SYSTEM_PROMPT}\nFecha actual: {fecha_hoy}\nUsuario: {texto_usuario}"
    try:
        respuesta = model.generate_content(prompt_completo).text.strip()
    except Exception as e:
        print(f"Error Gemini: {e}")
        respuesta = "Ocurrió un error procesando la inteligencia artificial."
    return _responder(respuesta, al_responder)


def ejecutar_ciclo_unico(al_escuchar=None, al_usuario=None, al_responder=None):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.pause_threshold = 2.0
    r.non_speaking_duration = 0.8

    try:
        with sr.Microphone(device_index=MIC_INDEX) as source:
            print("Calibrando ruido... quédate en silencio un segundo")
            r.adjust_for_ambient_noise(source, duration=1)
            r.energy_threshold = max(r.energy_threshold, UMBRAL_MINIMO)
            print(f"Umbral de voz: {r.energy_threshold:.0f}")
            if al_escuchar:
                al_escuchar()
            print("Escuchando...")
            audio = r.listen(source, timeout=8, phrase_time_limit=20)
        print("Audio capturado, reconociendo...")
    except sr.WaitTimeoutError:
        return _mensaje_rapido("No escuché nada, intenta de nuevo.", al_responder)
    except Exception as e:
        print(f"Error de micrófono: {e}")
        return _mensaje_rapido("No pude usar el micrófono.", al_responder)

    try:
        texto = r.recognize_google(audio, language="es-CO")
    except sr.UnknownValueError:
        return _mensaje_rapido("No te entendí.", al_responder)
    except Exception as e:
        print(f"Error de reconocimiento: {e}")
        return _mensaje_rapido("Ocurrió un error al escuchar.", al_responder)

    print(f"Usuario dijo: {texto}")
    if al_usuario:
        al_usuario(texto)

    respuesta = procesar_texto_ia_streaming(texto, al_responder)
    return texto, respuesta


if __name__ == "__main__":
    ejecutar_ciclo_unico()
