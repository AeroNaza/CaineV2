from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import prueba_voz
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'caine-v2-secret-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

usuario_hablando = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('iniciar_voz')
def handle_voz():
    global usuario_hablando

    if usuario_hablando:
        emit('error', {'mensaje': 'Ya hay una grabación en curso'})
        return

    usuario_hablando = True
    emit('estado_cambio', {'estado': 'escuchando'}, to=None)

    def ejecutar_voz():
        try:
            texto, respuesta = prueba_voz.ejecutar_ciclo_unico()

            socketio.emit('resultado_voz', {
                'usuario': texto,
                'respuesta': respuesta,
                'timestamp': datetime.now().strftime('%H:%M')
            }, to=None)

        except Exception as e:
            socketio.emit('error', {'mensaje': str(e)}, to=None)
        finally:
            usuario_hablando = False
            socketio.emit('estado_cambio', {'estado': 'listo'}, to=None)

    thread = threading.Thread(target=ejecutar_voz)
    thread.daemon = True
    thread.start()

@socketio.on('enviar_texto')
def handle_texto(data):
    texto_usuario = data.get('texto', '').strip()

    if not texto_usuario:
        emit('error', {'mensaje': 'Escribe algo primero'})
        return

    emit('estado_cambio', {'estado': 'procesando'}, to=None)

    def ejecutar_texto():
        try:
            respuesta = prueba_voz.procesar_texto_ia_streaming(texto_usuario)

            socketio.emit('resultado_texto', {
                'usuario': texto_usuario,
                'respuesta': respuesta,
                'timestamp': datetime.now().strftime('%H:%M')
            }, to=None)

        except Exception as e:
            socketio.emit('error', {'mensaje': str(e)}, to=None)
        finally:
            socketio.emit('estado_cambio', {'estado': 'listo'}, to=None)

    thread = threading.Thread(target=ejecutar_texto)
    thread.daemon = True
    thread.start()

@socketio.on('connect')
def handle_connect():
    print("Cliente conectado")
    emit('conectado', {'data': 'Conectado a Caine V2'})

if __name__ == '__main__':
    print("🚀 Servidor Caine V2 corriendo en http://localhost:5000")
    print("Presiona Ctrl+C para detener")
    socketio.run(app, host='localhost', port=5000, debug=False)
