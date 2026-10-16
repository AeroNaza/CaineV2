import asyncio
import os
from edge_tts import Communicate

VOZ = "es-ES-AlvaroNeural"
VELOCIDAD = "+8%"
ARCHIVO = "temp_caine.mp3"

async def _generar(texto):
    comunicador = Communicate(text=texto, voice=VOZ, rate=VELOCIDAD)
    await comunicador.save(ARCHIVO)

def hablar_sync(texto):
    texto = (texto or "").strip()
    if not texto:
        return
    try:
        asyncio.run(_generar(texto))
        if os.path.exists(ARCHIVO) and os.path.getsize(ARCHIVO) > 0:
            os.system(f"ffplay -nodisp -autoexit -loglevel quiet {ARCHIVO}")
        else:
            print("Error en audio: el archivo salió vacío")
    except Exception as e:
        print(f"Error en audio: {e}")
    finally:
        if os.path.exists(ARCHIVO):
            os.remove(ARCHIVO)
