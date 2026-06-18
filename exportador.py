

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


class ExportadorExcel:


    # (clave del diccionario, título de la columna en Excel). El orden de esta
    # lista define el orden de las columnas en la planilla.
    COLUMNAS = [
        ("inicio_dia", "Fecha"),
        ("inicio_hora", "Hora inicio"),
        ("fin_hora", "Hora fin"),
        ("punto", "Ubicación (Access Point)"),
        ("mac_ap", "MAC del AP"),
        ("session_time", "Duración (seg)"),
        ("input_bytes", "Entrada (bytes)"),
        ("output_bytes", "Salida (bytes)"),
        ("mac_cliente", "MAC del dispositivo"),
    ]

    def exportar(self, registros, usuario, desde, hasta, repositorio, ruta_salida):

        libro = Workbook()
        hoja = libro.active
        hoja.title = "Seguimiento"

        # --- Fila de título (información del seguimiento) ---
        hoja.append([f"Seguimiento del usuario: {usuario}"])
        hoja.append([f"Rango de fechas: {desde} a {hasta}"])
        hoja.append([f"Total de conexiones: {len(registros)}"])
        hoja.append([])   # fila en blanco de separación

        # --- Fila de encabezados (en negrita) ---
        fila_titulos = [titulo for _, titulo in self.COLUMNAS]
        hoja.append(fila_titulos)
        nro_fila_titulos = hoja.max_row
        for celda in hoja[nro_fila_titulos]:
            celda.font = Font(bold=True)
            celda.alignment = Alignment(horizontal="center")

        # --- Filas de datos ---
        for r in registros:
            # agregamos al diccionario el nombre corto del punto (Access Point)
            r_punto = dict(r)
            r_punto["punto"] = repositorio.etiqueta(r["mac_ap"])
            hoja.append([r_punto[clave] for clave, _ in self.COLUMNAS])

        # --- Ajuste de ancho de columnas para que se lea cómodo ---
        anchos = [12, 12, 12, 18, 24, 14, 16, 16, 22]
        for indice, ancho in enumerate(anchos, start=1):
            letra = hoja.cell(row=1, column=indice).column_letter
            hoja.column_dimensions[letra].width = ancho

        libro.save(ruta_salida)
        return ruta_salida
