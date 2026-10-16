import threading
import queue
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import prueba_voz
from puerto_serie import gestor, listar_puertos

FONDO = "#030604"
PANEL = "#08100a"
BORDE = "#16361f"
VERDE = "#4dff7a"
VERDE_MED = "#2fb35a"
VERDE_OSC = "#0d3a1c"
GRIS = "#557a60"
BLANCO = "#dcffe4"
ROJO = "#ff6b6b"
AMBAR = "#ffcc66"
FUENTE = "Monospace"
BAUDIOS = [9600, 19200, 38400, 57600, 115200, 230400]

# Sprite de Caine: 16x16
# x = contorno   d = relleno   e = ojos   m = boca   O = interior de la boca
PX = 12
PALETA = {"x": VERDE, "d": "#0c3d1d", "e": BLANCO, "m": VERDE, "O": "#000000"}
FILAS_BASE = [
    "......xxxx......",
    "...xxddddddxx...",
    "..xxddddddddxx..",
    ".xxddddddddddxx.",
    ".xddddddddddddx.",
    ".xddddddddddddx.",
    "xxddddddddddddxx",
    "xxddddddddddddxx",
    "xxddddddddddddxx",
    ".xddddddddddddx.",
    ".xdddmmmmmmdddx.",
    ".xddddddddddddx.",
    "..xxddddddddxx..",
    "....xxxxxxxx....",
    "................",
    "................",
]
RELLENO = ".xddddddddddddx."
BOCA_CERRADA = ".xdddmmmmmmdddx."


class CaineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAINE")
        self.geometry("1280x760")
        self.minsize(1000, 640)
        self.configure(bg=FONDO)
        self.option_add("*TCombobox*Listbox.background", PANEL)
        self.option_add("*TCombobox*Listbox.foreground", VERDE)
        self.option_add("*TCombobox*Listbox.selectBackground", VERDE_OSC)
        self.option_add("*TCombobox*Listbox.selectForeground", VERDE)
        self.bind("<F11>", self._alternar_pantalla)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self.cola = queue.Queue()
        self.estado = "reposo"
        self.paso = 0
        self.ocupado = False
        self._conectando = False

        self._estilo()
        self._construir()
        self.after(50, self._procesar_cola)
        self.after(160, self._animar)
        self.after(1000, self._reloj)

        self.log("Sistema listo. Elige un puerto, conéctalo y escribe o presiona HABLAR.", "sistema")
        self.refrescar_puertos()
        self._actualizar_serie()
        self.entrada.focus_set()

    # ---------- estilo ----------

    def _estilo(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Caine.TCombobox", fieldbackground=PANEL, background=VERDE_OSC,
                         foreground=VERDE, arrowcolor=VERDE, bordercolor=BORDE,
                         lightcolor=PANEL, darkcolor=PANEL, selectbackground=VERDE_OSC,
                         selectforeground=VERDE)
        estilo.map("Caine.TCombobox",
                   fieldbackground=[("readonly", PANEL)],
                   foreground=[("readonly", VERDE)],
                   selectbackground=[("readonly", PANEL)],
                   selectforeground=[("readonly", VERDE)])

    # ---------- construcción ----------

    def _construir(self):
        # Cabecera
        cab = tk.Frame(self, bg=FONDO)
        cab.pack(side="top", fill="x", padx=24, pady=(16, 10))
        tk.Label(cab, text="CAINE", fg=VERDE, bg=FONDO,
                 font=(FUENTE, 20, "bold")).pack(side="left")
        tk.Label(cab, text="  asistente virtual", fg=GRIS, bg=FONDO,
                 font=(FUENTE, 10)).pack(side="left", pady=(8, 0))
        self.lbl_reloj = tk.Label(cab, text="", fg=GRIS, bg=FONDO, font=(FUENTE, 10))
        self.lbl_reloj.pack(side="right")
        self.lbl_cab_serie = tk.Label(cab, text="", fg=GRIS, bg=FONDO,
                                      font=(FUENTE, 10, "bold"))
        self.lbl_cab_serie.pack(side="right", padx=24)

        # Pie: entrada y botones de voz y texto
        pie = tk.Frame(self, bg=FONDO)
        pie.pack(side="bottom", fill="x", padx=24, pady=(8, 18))
        tk.Label(pie, text=">", fg=VERDE, bg=FONDO,
                 font=(FUENTE, 16, "bold")).pack(side="left", padx=(0, 10))
        self.entrada = tk.Entry(pie, bg=PANEL, fg=VERDE, insertbackground=VERDE,
                                font=(FUENTE, 12), bd=0, relief="flat",
                                highlightthickness=1, highlightbackground=BORDE,
                                highlightcolor=VERDE_MED)
        self.entrada.pack(side="left", fill="x", expand=True, ipady=8)
        self.entrada.bind("<Return>", lambda e: self.enviar_texto())

        self.btn_enviar = self._boton(pie, "ENVIAR", self.enviar_texto)
        self.btn_enviar.pack(side="right", padx=(10, 0))
        self.btn_voz = self._boton(pie, "HABLAR", self.iniciar_voz)
        self.btn_voz.pack(side="right", padx=(10, 0))

        # Cuerpo
        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(side="top", fill="both", expand=True, padx=24, pady=(0, 6))

        # Columna izquierda: registro
        marco_chat, zona_chat = self._tarjeta(cuerpo, "REGISTRO")
        marco_chat.pack(side="left", fill="both", expand=True, padx=(0, 16))

        self.chat = tk.Text(zona_chat, bg=PANEL, fg=VERDE, font=(FUENTE, 12),
                            wrap="word", bd=0, padx=16, pady=12, state="disabled",
                            highlightthickness=0, spacing1=2, spacing3=2)
        scroll = tk.Scrollbar(zona_chat, command=self.chat.yview, width=10,
                              bg=VERDE_OSC, troughcolor=PANEL, activebackground=VERDE_MED)
        self.chat.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat.pack(side="left", fill="both", expand=True)
        self.chat.tag_configure("hora", foreground=GRIS)
        self.chat.tag_configure("usuario", foreground=BLANCO)
        self.chat.tag_configure("caine", foreground=VERDE)
        self.chat.tag_configure("sistema", foreground=GRIS)
        self.chat.tag_configure("error", foreground=ROJO)

        # Columna derecha: Caine + puerto serie
        derecha = tk.Frame(cuerpo, bg=FONDO, width=300)
        derecha.pack(side="right", fill="y")
        derecha.pack_propagate(False)

        marco_caine, zona_caine = self._tarjeta(derecha, "CAINE")
        marco_caine.pack(fill="x")
        self.sprite = tk.Canvas(zona_caine, width=16 * PX, height=16 * PX, bg=PANEL,
                                highlightthickness=0)
        self.sprite.pack(pady=(24, 12))
        self.lbl_estado = tk.Label(zona_caine, text="EN REPOSO", fg=VERDE, bg=PANEL,
                                   font=(FUENTE, 11, "bold"))
        self.lbl_estado.pack(pady=(0, 22))

        marco_serie, zona_serie = self._tarjeta(derecha, "PUERTO SERIE")
        marco_serie.pack(fill="x", pady=(16, 0))

        tk.Label(zona_serie, text="PUERTO", fg=GRIS, bg=PANEL,
                 font=(FUENTE, 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.cb_puerto = ttk.Combobox(zona_serie, state="readonly", style="Caine.TCombobox")
        self.cb_puerto.pack(fill="x", padx=14)

        tk.Label(zona_serie, text="BAUDIOS", fg=GRIS, bg=PANEL,
                 font=(FUENTE, 9, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.cb_baud = ttk.Combobox(zona_serie, values=BAUDIOS, state="readonly",
                                    style="Caine.TCombobox")
        self.cb_baud.set(115200)
        self.cb_baud.pack(fill="x", padx=14)

        fila = tk.Frame(zona_serie, bg=PANEL)
        fila.pack(fill="x", padx=14, pady=(16, 8))
        self.btn_actualizar = self._boton(fila, "ACTUALIZAR", self.refrescar_puertos, pequeno=True)
        self.btn_actualizar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.btn_conexion = self._boton(fila, "CONECTAR", self.alternar_conexion, pequeno=True)
        self.btn_conexion.pack(side="left", fill="x", expand=True)

        self.lbl_serie = tk.Label(zona_serie, text="", fg=GRIS, bg=PANEL, font=(FUENTE, 9),
                                  justify="left", wraplength=260)
        self.lbl_serie.pack(anchor="w", padx=14, pady=(4, 14))

    def _tarjeta(self, padre, titulo):
        marco = tk.Frame(padre, bg=BORDE, padx=1, pady=1)
        cabecera = tk.Frame(marco, bg=PANEL)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text=f" {titulo} ", fg=GRIS, bg=PANEL,
                 font=(FUENTE, 9, "bold")).pack(side="left", pady=6)
        zona = tk.Frame(marco, bg=PANEL)
        zona.pack(fill="both", expand=True)
        return marco, zona

    def _boton(self, padre, texto, comando, pequeno=False):
        tamano = 9 if pequeno else 11
        return tk.Button(padre, text=texto, command=comando, bg=VERDE_OSC, fg=VERDE,
                         activebackground=VERDE_MED, activeforeground=FONDO,
                         font=(FUENTE, tamano, "bold"), bd=0, relief="flat",
                         padx=14, pady=7 if not pequeno else 5, cursor="hand2")

    # ---------- utilidades ----------

    def _alternar_pantalla(self, _=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def _reloj(self):
        self.lbl_reloj.configure(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.after(1000, self._reloj)

    def _main(self, fn, *args):
        """Desde hilos secundarios: encola la acción para el hilo principal."""
        self.cola.put(lambda: fn(*args))

    def _procesar_cola(self):
        try:
            while True:
                self.cola.get_nowait()()
        except queue.Empty:
            pass
        self.after(50, self._procesar_cola)

    def log(self, texto, tipo="sistema"):
        prefijos = {"usuario": "TU    ", "caine": "CAINE  ", "sistema": "SYS   ", "error": "ERR   "}
        hora = datetime.now().strftime("%H:%M")
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{hora}  ", "hora")
        self.chat.insert("end", prefijos[tipo], tipo)
        self.chat.insert("end", f"{texto}\n", tipo)
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _set_estado(self, estado):
        self.estado = estado
        textos = {"reposo": "EN REPOSO", "escuchando": "ESCUCHANDO",
                  "pensando": "PROCESANDO", "hablando": "HABLANDO"}
        self.lbl_estado.configure(text=textos[estado])

    def _ocupar(self, estado):
        self.ocupado = True
        self._set_estado(estado)

    def _liberar(self):
        self.ocupado = False
        self._set_estado("reposo")
        self.entrada.focus_set()

    def _mostrar_respuesta(self, respuesta):
        self.log(respuesta, "caine")
        self._set_estado("hablando")

    def _cerrar(self):
        gestor.desconectar()
        self.destroy()

    # ---------- puerto serie ----------

    def refrescar_puertos(self):
        puertos = listar_puertos()
        if puertos:
            self.cb_puerto["values"] = puertos
            preferido = "/dev/ttyACM0" if "/dev/ttyACM0" in puertos else puertos[0]
            self.cb_puerto.set(preferido)
            self.log(f"{len(puertos)} puerto(s) encontrados.", "sistema")
        else:
            self.cb_puerto["values"] = []
            self.cb_puerto.set("(sin puertos)")
            self.log("No hay puertos disponibles. Conecta la micro:bit y pulsa ACTUALIZAR.", "error")

    def _actualizar_serie(self):
        if gestor.conectado():
            resumen = f"CONECTADO  {gestor.puerto}"
            detalle = f"{gestor.puerto} a {gestor.baudios} baudios"
            color = VERDE
            self.btn_conexion.configure(text="DESCONECTAR")
        else:
            resumen = "SIN CONEXIÓN"
            detalle = "Elige puerto y baudios, luego pulsa CONECTAR."
            color = GRIS
            self.btn_conexion.configure(text="CONECTAR")
        self.lbl_serie.configure(text=detalle, fg=color)
        self.lbl_cab_serie.configure(text=resumen, fg=color)

    def alternar_conexion(self):
        if gestor.conectado():
            gestor.desconectar()
            self.log("Caine se desconectó del puerto.", "sistema")
            self._actualizar_serie()
            return
        if self._conectando:
            return
        puerto = self.cb_puerto.get().strip()
        if not puerto or puerto.startswith("("):
            self.log("Elige un puerto de la lista primero.", "error")
            return
        try:
            baud = int(self.cb_baud.get())
        except ValueError:
            self.log("Los baudios no son válidos.", "error")
            return
        self._conectando = True
        self.lbl_serie.configure(text="Conectando...", fg=AMBAR)
        self.lbl_cab_serie.configure(text="CONECTANDO", fg=AMBAR)
        threading.Thread(target=self._hilo_conectar, args=(puerto, baud), daemon=True).start()

    def _hilo_conectar(self, puerto, baud):
        try:
            gestor.conectar(puerto, baud)
            self._main(self.log, f"Caine conectado a {puerto} a {baud} baudios.", "sistema")
        except Exception as e:
            self._main(self.log, f"No pude abrir {puerto}: {e}", "error")
        finally:
            self._main(self._fin_conexion)

    def _fin_conexion(self):
        self._conectando = False
        self._actualizar_serie()

    # ---------- voz ----------

    def iniciar_voz(self):
        if self.ocupado:
            self.log("Caine está ocupado, espera un momento.", "sistema")
            return
        self._ocupar("escuchando")
        threading.Thread(target=self._hilo_voz, daemon=True).start()

    def _hilo_voz(self):
        try:
            prueba_voz.ejecutar_ciclo_unico(
                al_escuchar=lambda: self._main(self._set_estado, "escuchando"),
                al_usuario=lambda t: self._main(self.log, t, "usuario"),
                al_responder=lambda r: self._main(self._mostrar_respuesta, r),
            )
        except Exception as e:
            self._main(self.log, f"Error: {e}", "error")
        finally:
            self._main(self._liberar)

    # ---------- texto ----------

    def enviar_texto(self):
        if self.ocupado:
            self.log("Caine está ocupado, espera un momento.", "sistema")
            return
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.entrada.delete(0, "end")
        self.log(texto, "usuario")
        self._ocupar("pensando")
        threading.Thread(target=self._hilo_texto, args=(texto,), daemon=True).start()

    def _hilo_texto(self, texto):
        try:
            prueba_voz.procesar_texto_ia_streaming(
                texto,
                al_responder=lambda r: self._main(self._mostrar_respuesta, r),
            )
        except Exception as e:
            self._main(self.log, f"Error: {e}", "error")
        finally:
            self._main(self._liberar)

    # ---------- personaje ----------

    def _animar(self):
        self.paso = (self.paso + 1) % 1000
        self._dibujar()
        self.after(160, self._animar)

    def _boca(self):
        if self.estado == "hablando":
            ciclo = [
                (BOCA_CERRADA, RELLENO),
                (BOCA_CERRADA, ".xdddmOOOOmdddx."),
                (BOCA_CERRADA, ".xddmOOOOOOmddx."),
                (BOCA_CERRADA, ".xdddmOOOOmdddx."),
            ]
            return ciclo[self.paso % len(ciclo)]
        if self.estado == "escuchando":
            return (".xddddmOOmddddx.", RELLENO)
        if self.estado == "pensando":
            return (".xdddddmmmmdddx.", RELLENO)
        return (BOCA_CERRADA, RELLENO)

    def _filas_ojos(self):
        if self.estado == "escuchando":
            return [5, 6, 7]
        if self.estado == "pensando":
            return [6]
        if self.estado == "reposo":
            return [7]
        # Parpadeo ocasional mientras habla o está en reposo
        if self.paso % 30 == 0:
            return [7]
        return [6, 7]

    def _dibujar(self):
        c = self.sprite
        c.delete("all")

        filas = [list(f.ljust(16, ".")[:16]) for f in FILAS_BASE]

        arriba, abajo = self._boca()
        filas[10] = list(arriba.ljust(16, ".")[:16])
        filas[11] = list(abajo.ljust(16, ".")[:16])

        for y in self._filas_ojos():
            for x in (4, 5, 10, 11):
                filas[y][x] = "e"

        if self.estado == "pensando":
            for i in range(self.paso % 4):
                if i < 3:
                    filas[0][12 + i] = "e"

        for y, fila in enumerate(filas):
            for x, ch in enumerate(fila):
                color = PALETA.get(ch)
                if color:
                    c.create_rectangle(x * PX, y * PX, (x + 1) * PX, (y + 1) * PX,
                                       fill=color, outline="")


if __name__ == "__main__":
    app = CaineApp()
    app.mainloop()
