import time
import threading
import serial
import serial.tools.list_ports


def listar_puertos():
    puertos = [p.device for p in serial.tools.list_ports.comports()]
    prioritarios = [p for p in puertos if "ACM" in p or "USB" in p]
    otros = [p for p in puertos if p not in prioritarios]
    return prioritarios + otros


class GestorSerial:
    def __init__(self):
        self._ser = None
        self._lock = threading.Lock()
        self.puerto = None
        self.baudios = None

    def conectado(self):
        return self._ser is not None and self._ser.is_open

    def conectar(self, puerto, baudios):
        self.desconectar()
        ser = serial.Serial(puerto, baudios, timeout=1)
        time.sleep(2)  # la micro:bit se reinicia al abrir el puerto
        with self._lock:
            self._ser = ser
            self.puerto = puerto
            self.baudios = baudios

    def desconectar(self):
        with self._lock:
            if self._ser is not None:
                try:
                    self._ser.close()
                except Exception:
                    pass
            self._ser = None
            self.puerto = None
            self.baudios = None

    def enviar(self, texto):
        with self._lock:
            if not self.conectado():
                return False
            try:
                self._ser.write((texto + "\n").encode("utf-8"))
                self._ser.flush()
                return True
            except Exception as e:
                print(f"Error serial: {e}")
                return False


gestor = GestorSerial()
