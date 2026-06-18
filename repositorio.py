"""
repositorio.py
--------------
Se encarga de leer el archivo CSV, validar cada registro con el ValidadorRegistro
y guardar en memoria:
    - los registros VÁLIDOS  -> en una lista de diccionarios (como pide el TP)
    - los registros DESCARTADOS -> en otra lista, para mostrarlos al final

También ofrece las consultas que necesita la aplicación:
    - lista de usuarios distintos
    - seguimiento de un usuario en un rango de fechas
"""

import csv


class RepositorioConexiones:
    """Almacena los registros de conexión wifi y permite consultarlos."""

    def __init__(self, validador):
        # Recibe el validador "desde afuera" (inyección de dependencia):
        # así el repositorio no sabe NADA de regex, solo le pregunta si una
        # fila es válida. Cada clase tiene una única responsabilidad.
        self.validador = validador
        self.registros = []      # lista de diccionarios -> registros válidos
        self.descartados = []    # lista de tuplas (nro_linea, motivo, fila)
        self.etiquetas_ap = {}   # MAC_AP -> nombre corto ("Punto 01", ...)

    def cargar(self, ruta_csv):
        """Lee el CSV línea por línea, valida cada fila y la guarda donde
        corresponda. Devuelve la cantidad total de filas leídas."""
        total = 0
        with open(ruta_csv, encoding="utf-8", newline="") as archivo:
            lector = csv.reader(archivo)
            next(lector)            # salteamos la primera fila (los títulos)
            numero_linea = 1
            for fila in lector:
                numero_linea += 1
                total += 1
                es_valido, motivo = self.validador.validar(fila)
                if es_valido:
                    self.registros.append(self._a_diccionario(fila))
                else:
                    self.descartados.append((numero_linea, motivo, fila))

        # Una vez cargados los válidos, armamos nombres cortos para cada AP.
        self._armar_etiquetas_ap()
        return total

    def _a_diccionario(self, fila):
        """Convierte una fila válida (lista) en un diccionario con nombres
        claros. Los campos numéricos se pasan a int para poder operarlos."""
        return {
            "usuario": fila[3].strip(),
            "ip_ap": fila[4].strip(),
            "inicio_dia": fila[6].strip(),
            "inicio_hora": fila[7].strip(),
            "fin_dia": fila[8].strip(),
            "fin_hora": fila[9].strip(),
            "session_time": int(fila[10].strip()),   # segundos
            "input_bytes": int(fila[11].strip()),     # bytes
            "output_bytes": int(fila[12].strip()),    # bytes
            "mac_ap": fila[13].strip(),
            "mac_cliente": fila[14].strip(),
        }

    def _armar_etiquetas_ap(self):
        """A cada Access Point distinto le asignamos un nombre corto y estable
        ("Punto 01", "Punto 02", ...). La MAC_AP es difícil de leer; estos
        nombres hacen mucho más claro el 'recorrido' del usuario."""
        macs_distintas = sorted({r["mac_ap"] for r in self.registros})
        for indice, mac in enumerate(macs_distintas, start=1):
            self.etiquetas_ap[mac] = f"Punto {indice:02d}"

    def usuarios(self):
        """Devuelve la lista ordenada de usuarios distintos (para el filtro)."""
        return sorted({r["usuario"] for r in self.registros})

    def seguimiento(self, usuario, fecha_desde, fecha_hasta):
        """Devuelve los registros de un usuario dentro de un rango de fechas,
        ordenados cronológicamente.

        Truco: como las fechas tienen formato AAAA-MM-DD, compararlas como
        texto da el mismo resultado que compararlas como fechas reales
        (orden alfabético = orden cronológico). Por eso no necesitamos
        convertirlas a objetos de fecha.
        """
        resultado = [
            r for r in self.registros
            if r["usuario"] == usuario
            and fecha_desde <= r["inicio_dia"] <= fecha_hasta
        ]
        # Ordenamos por día y, dentro del día, por hora de inicio.
        resultado.sort(key=lambda r: (r["inicio_dia"], r["inicio_hora"]))
        return resultado

    def etiqueta(self, mac_ap):
        """Devuelve el nombre corto de un Access Point (o la MAC si no está)."""
        return self.etiquetas_ap.get(mac_ap, mac_ap)
