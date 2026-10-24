"""Ventana de demostración (Tkinter) para probar el sistema de forma visual.

No es parte de la entrega: la especificación pide una CLI y deja la interfaz
gráfica fuera de alcance. Usa el mismo `Servicio` que la CLI, así que aplica
exactamente las mismas reglas.

Uso: python3 gui_demo.py [--db RUTA]
"""

import argparse
import tkinter as tk
from tkinter import ttk

from dominio import FORMATO_FECHA_HORA, ErrorValidacion
from inventario import cargar_inventario
from repositorio import RUTA_DB, Repositorio
from servicio import ErrorReserva, Servicio

COLUMNAS = ("id", "unidad", "inicio", "fin", "solicitante", "estado")
COLOR_OK = "#1a7f37"
COLOR_ERROR = "#cf222e"


class App:
    def __init__(self, raiz: tk.Tk, servicio: Servicio):
        self.raiz = raiz
        self.servicio = servicio
        raiz.title("Reservas de laboratorio (demo)")

        self.unidad = tk.StringVar()
        self.solicitante = tk.StringVar()
        self.inicio = tk.StringVar(value="2026-11-02 10:00")
        self.fin = tk.StringVar(value="2026-11-02 11:00")
        self.mensaje = tk.StringVar()

        marco = ttk.Frame(raiz, padding=12)
        marco.grid(sticky="nsew")
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)

        formulario = ttk.LabelFrame(marco, text="Nueva reserva", padding=8)
        formulario.grid(row=0, column=0, sticky="ew")

        unidades = servicio.unidades()
        ttk.Label(formulario, text="Unidad").grid(row=0, column=0, sticky="w")
        self.selector_unidad = ttk.Combobox(
            formulario,
            textvariable=self.unidad,
            values=[u.id for u in unidades],
            state="readonly",
            width=12,
        )
        self.selector_unidad.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.selector_unidad.current(0)
        equipos = {u.id: u.equipo for u in unidades}
        self.equipo = ttk.Label(formulario, text=equipos[self.unidad.get()])
        self.equipo.grid(row=0, column=2, sticky="w")
        self.selector_unidad.bind(
            "<<ComboboxSelected>>",
            lambda _: self.equipo.config(text=equipos[self.unidad.get()]),
        )

        campos = [
            ("Solicitante", self.solicitante),
            ("Inicio (YYYY-MM-DD HH:MM)", self.inicio),
            ("Fin (YYYY-MM-DD HH:MM)", self.fin),
        ]
        for fila, (texto, variable) in enumerate(campos, start=1):
            ttk.Label(formulario, text=texto).grid(row=fila, column=0, sticky="w")
            ttk.Entry(formulario, textvariable=variable, width=24).grid(
                row=fila, column=1, columnspan=2, sticky="w", padx=4, pady=2
            )

        botones = ttk.Frame(formulario)
        botones.grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Button(botones, text="Consultar disponibilidad", command=self.consultar).grid(
            row=0, column=0
        )
        ttk.Button(botones, text="Reservar", command=self.reservar).grid(
            row=0, column=1, padx=6
        )

        self.etiqueta_mensaje = tk.Label(
            marco, textvariable=self.mensaje, anchor="w", justify="left", wraplength=620
        )
        self.etiqueta_mensaje.grid(row=1, column=0, sticky="ew", pady=8)

        listado = ttk.LabelFrame(marco, text="Reservas", padding=8)
        listado.grid(row=2, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(2, weight=1)

        self.tabla = ttk.Treeview(listado, columns=COLUMNAS, show="headings", height=8)
        anchos = {"id": 40, "unidad": 70, "inicio": 130, "fin": 130, "solicitante": 140, "estado": 80}
        for columna in COLUMNAS:
            self.tabla.heading(columna, text=columna.capitalize())
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)

        ttk.Button(
            listado, text="Cancelar seleccionada", command=self.cancelar_seleccionada
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.refrescar()

    def refrescar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for r in self.servicio.listar():
            self.tabla.insert(
                "",
                "end",
                iid=str(r.id),
                values=(
                    r.id,
                    r.unidad,
                    r.inicio.strftime(FORMATO_FECHA_HORA),
                    r.fin.strftime(FORMATO_FECHA_HORA),
                    r.solicitante,
                    r.estado,
                ),
            )

    def consultar(self) -> None:
        def accion():
            bloqueantes = self.servicio.consultar_disponibilidad(
                self.unidad.get(), self.inicio.get(), self.fin.get()
            )
            rango = f"de {self.inicio.get()} a {self.fin.get()}"
            if not bloqueantes:
                return f"{self.unidad.get()} disponible {rango}."
            ids = ", ".join(f"#{r.id}" for r in bloqueantes)
            return f"{self.unidad.get()} no disponible {rango}. Ocupada por {ids}."

        self._ejecutar(accion)

    def reservar(self) -> None:
        def accion():
            r = self.servicio.reservar(
                self.unidad.get(), self.solicitante.get(), self.inicio.get(), self.fin.get()
            )
            return f"Reserva {r.id} creada para {r.unidad}."

        self._ejecutar(accion)

    def cancelar_seleccionada(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            self._mostrar("Seleccioná una reserva en la tabla.", COLOR_ERROR)
            return
        id_reserva = int(seleccion[0])
        self._ejecutar(lambda: f"Reserva {self.servicio.cancelar(id_reserva).id} cancelada.")

    def _ejecutar(self, accion) -> None:
        try:
            texto = accion()
        except (ErrorValidacion, ErrorReserva) as error:
            self._mostrar(f"Error: {error}", COLOR_ERROR)
            return
        self._mostrar(texto, COLOR_OK)
        self.refrescar()

    def _mostrar(self, texto: str, color: str) -> None:
        self.mensaje.set(texto)
        self.etiqueta_mensaje.config(fg=color)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Ventana de demostración.")
    parser.add_argument("--db", default=str(RUTA_DB))
    args = parser.parse_args(argv)
    raiz = tk.Tk()
    with Repositorio(args.db) as repo:
        App(raiz, Servicio(repo, cargar_inventario()))
        raiz.mainloop()


if __name__ == "__main__":
    main()
