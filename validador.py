

import re


class ValidadorRegistro:
    """Valida un registro (una fila del CSV) campo por campo con regex.

    Si TODOS los campos cumplen su patrón y ninguno está vacío, el registro
    es válido. Si alguno falla, el registro se descarta.
    """

    def __init__(self):
        # Compilamos cada expresión regular UNA sola vez (con re.compile).
        # Como vamos a validar un millón de filas, compilar una vez y reusar
        # es mucho más eficiente que recompilar en cada fila.

        # Fecha: 4 dígitos - 2 dígitos - 2 dígitos   ->  2019-02-07
        self.re_fecha = re.compile(r"\d{4}-\d{2}-\d{2}")

        # Hora: 2 dígitos : 2 dígitos : 2 dígitos     ->  19:46:08
        self.re_hora = re.compile(r"\d{2}:\d{2}:\d{2}")

        # Entero no negativo: uno o más dígitos       ->  25, 39517, 0
        self.re_entero = re.compile(r"\d+")

        # MAC del Access Point: 6 pares hexadecimales separados por "-" y
        # terminada en ":HCDD"                        ->  DC-9F-DB-12-F3-EA:HCDD
        #   ([0-9A-Fa-f]{2}-){5}  -> cinco veces "par_hex-"
        #   [0-9A-Fa-f]{2}        -> el último par hex
        #   :HCDD                 -> el sufijo fijo
        self.re_mac_ap = re.compile(r"([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}:HCDD")

        # MAC del dispositivo cliente: 6 pares hex, sin sufijo
        #                                             ->  DC-BF-E9-1A-B5-D0
        self.re_mac = re.compile(r"([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}")

        # Usuario: uno o más caracteres alfanuméricos, punto, guion o guion bajo
        #   \w  = letra, dígito o "_"   |   . y \- = punto y guion literales
        self.re_usuario = re.compile(r"[\w.\-]+")

        # Tipo de conexión: el texto exacto "Wireless-802.11"
        #   El \. escapa el punto para que signifique un punto literal y no
        #   "cualquier carácter".
        self.re_tipo = re.compile(r"Wireless-802\.11")

    def validar(self, fila):
        """Recibe una fila (lista de columnas) y devuelve una tupla:
            (es_valido, motivo)
        donde 'es_valido' es True/False y 'motivo' explica el primer error
        encontrado (cadena vacía si el registro es válido).

        Usamos .fullmatch(): exige que TODA la cadena calce con el patrón,
        no solo un pedacito. Si no calza, devuelve None.
        """
        # Las filas corruptas suelen tener menos columnas de lo esperado.
        if len(fila) < 16:
            return (False, "fila incompleta (tiene menos de 16 columnas)")

        # Tomamos cada campo por su posición en el CSV y le sacamos espacios.
        usuario = fila[3].strip()
        tipo = fila[5].strip()
        inicio_dia = fila[6].strip()
        inicio_hora = fila[7].strip()
        fin_dia = fila[8].strip()
        fin_hora = fila[9].strip()
        session_time = fila[10].strip()
        input_octets = fila[11].strip()
        output_octets = fila[12].strip()
        mac_ap = fila[13].strip()
        mac_cliente = fila[14].strip()

        # Lista de (valor a chequear, patrón que debe cumplir, nombre del campo).
        # La recorremos en orden; el primero que falle corta y reporta el motivo.
        chequeos = [
            (usuario, self.re_usuario, "Usuario"),
            (tipo, self.re_tipo, "Tipo_conexion"),
            (inicio_dia, self.re_fecha, "Inicio_Dia"),
            (inicio_hora, self.re_hora, "Inicio_Hora"),
            (fin_dia, self.re_fecha, "Fin_Dia"),
            (fin_hora, self.re_hora, "Fin_Hora"),
            (session_time, self.re_entero, "Session_Time"),
            (input_octets, self.re_entero, "Input_Octects"),
            (output_octets, self.re_entero, "Output_Octects"),
            (mac_ap, self.re_mac_ap, "MAC_AP"),
            (mac_cliente, self.re_mac, "MAC_Cliente"),
        ]

        for valor, patron, nombre in chequeos:
            # Falla si el campo está vacío o si la regex no acepta la cadena.
            if valor == "" or patron.fullmatch(valor) is None:
                return (False, f"campo {nombre} inválido o vacío: '{valor}'")

        return (True, "")
