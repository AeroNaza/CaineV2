import serial
import time

PORT = "/dev/ttyACM0"
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"No se pudo conectar a la micro:bit: {e}")
    ser = None

def enviar_orden(estado):
    """
    Envía la orden ('A' o 'B') a la micro:bit si el puerto está activo.
    """
    if ser and ser.is_open:
        try:
            ser.write((estado + "\n").encode('utf-8'))
            ser.flush()
        except Exception as e:
            print(f"Error al enviar datos por serial: {e}")
