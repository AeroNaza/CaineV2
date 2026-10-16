const socket = io();
let microfono_activo = false;

const btnVoz = document.getElementById('btn-voz');
const btnEnviar = document.getElementById('btn-enviar');
const entradaTexto = document.getElementById('entrada-texto');
const historial = document.getElementById('historial');
const personaje = document.getElementById('personaje');
const estadoTexto = document.getElementById('estado-texto');
const conexionStatus = document.getElementById('conexion-status');
const boca = document.getElementById('boca');

socket.on('conectado', (data) => {
    console.log('Conectado al servidor:', data);
    actualizarEstado('Listo');
    conexionStatus.textContent = '● En línea';
    conexionStatus.classList.add('conectado');
});

socket.on('disconnect', () => {
    conexionStatus.textContent = '● Desconectado';
    conexionStatus.classList.remove('conectado');
    conexionStatus.classList.add('desconectado');
});

socket.on('estado_cambio', (data) => {
    actualizarEstado(data.estado);
    cambiarEstadoPersonaje(data.estado);
});

socket.on('resultado_voz', (data) => {
    if (data.usuario) {
        agregarMensaje(data.usuario, 'usuario', data.timestamp);
    }
    agregarMensaje(data.respuesta, 'respuesta', data.timestamp);
    animarHablando();
});

socket.on('resultado_texto', (data) => {
    agregarMensaje(data.usuario, 'usuario', data.timestamp);
    agregarMensaje(data.respuesta, 'respuesta', data.timestamp);
    animarHablando();
});

socket.on('error', (data) => {
    agregarMensaje(`Error: ${data.mensaje}`, 'sistema', new Date().toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'}));
    actualizarEstado('Error');
});

function actualizarEstado(nuevo_estado) {
    let texto = nuevo_estado.toUpperCase();

    switch(nuevo_estado.toLowerCase()) {
        case 'escuchando':
            texto = 'ESCUCHANDO...';
            break;
        case 'procesando':
            texto = 'PROCESANDO...';
            break;
        case 'hablando':
            texto = 'HABLANDO...';
            break;
        case 'listo':
            texto = 'LISTO';
            break;
    }

    estadoTexto.textContent = texto;
}

function cambiarEstadoPersonaje(estado) {
    personaje.classList.remove('pensativo', 'escuchando', 'hablando');

    switch(estado.toLowerCase()) {
        case 'escuchando':
            personaje.classList.add('escuchando');
            animarEscuchando();
            break;
        case 'procesando':
        case 'hablando':
            personaje.classList.add('hablando');
            animarHablando();
            break;
        default:
            personaje.classList.add('pensativo');
            boca.className = 'boca cerrada';
    }
}

function animarEscuchando() {
    boca.className = 'boca abierta1';
}

function animarHablando() {
    let frameActual = 0;
    const frames = ['cerrada', 'abierta1', 'abierta2'];

    const intervalo = setInterval(() => {
        boca.className = `boca ${frames[frameActual % frames.length]}`;
        frameActual++;
    }, 150);

    setTimeout(() => {
        clearInterval(intervalo);
        boca.className = 'boca cerrada';
    }, 5000);
}

function agregarMensaje(texto, tipo, timestamp) {
    const div = document.createElement('div');
    div.className = `mensaje ${tipo}`;

    let hora = timestamp || new Date().toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'});

    if (tipo === 'usuario') {
        div.innerHTML = `<span class="timestamp">[${hora}]</span> Tú: ${texto}`;
    } else if (tipo === 'respuesta') {
        div.innerHTML = `<span class="timestamp">[${hora}]</span> Caine: ${texto}`;
    } else {
        div.innerHTML = `<span class="timestamp">[${hora}]</span> ${texto}`;
    }

    historial.appendChild(div);
    historial.scrollTop = historial.scrollHeight;
}

btnVoz.addEventListener('click', () => {
    if (microfono_activo) return;

    microfono_activo = true;
    btnVoz.disabled = true;
    btnEnviar.disabled = true;
    entradaTexto.disabled = true;

    agregarMensaje('Iniciando micrófono...', 'sistema', new Date().toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'}));

    socket.emit('iniciar_voz');

    setTimeout(() => {
        microfono_activo = false;
        btnVoz.disabled = false;
        btnEnviar.disabled = false;
        entradaTexto.disabled = false;
    }, 12000);
});

btnEnviar.addEventListener('click', () => {
    enviarTexto();
});

entradaTexto.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        enviarTexto();
    }
});

function enviarTexto() {
    const texto = entradaTexto.value.trim();

    if (!texto) return;

    entradaTexto.value = '';
    btnVoz.disabled = true;
    btnEnviar.disabled = true;

    socket.emit('enviar_texto', { texto: texto });

    setTimeout(() => {
        btnVoz.disabled = false;
        btnEnviar.disabled = false;
    }, 3000);
}

window.addEventListener('load', () => {
    agregarMensaje('Sistema inicializado correctamente', 'sistema', new Date().toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'}));
    agregarMensaje('Esperando órdenes...', 'sistema', new Date().toLocaleTimeString('es-CO', {hour: '2-digit', minute:'2-digit'}));
});
