import os

from validador import ValidadorRegistro
from repositorio import RepositorioConexiones
from exportador import ExportadorExcel


# Nombre del archivo CSV. Debe estar en la misma carpeta que este programa.
ARCHIVO_CSV = "export-2019-to-now-v4.csv"


# ---------------------------------------------------------------------------
# Funciones auxiliares de la interfaz
# ---------------------------------------------------------------------------

def pedir_fecha(validador, mensaje):
    """Pide una fecha por teclado y la valida con la MISMA regex de fechas
    del validador. No deja avanzar hasta que el formato sea AAAA-MM-DD."""
    while True:
        valor = input(mensaje).strip()
        if validador.re_fecha.fullmatch(valor):
            return valor
        print("  Formato inválido. Usá AAAA-MM-DD (ejemplo: 2019-02-07).")


def elegir_usuario(repositorio):
    """Permite buscar y elegir un usuario de la lista. Devuelve el usuario
    elegido o None si el usuario cancela."""
    todos = repositorio.usuarios()
    while True:
        texto = input(
            "\nEscribí parte del nombre del usuario (Enter = ver todos, "
            "'x' = cancelar): "
        ).strip().lower()

        if texto == "x":
            return None

        # Filtramos los usuarios que contienen el texto buscado.
        if texto == "":
            coincidencias = todos
        else:
            coincidencias = [u for u in todos if texto in u.lower()]

        if not coincidencias:
            print("  No hay usuarios que coincidan. Probá de nuevo.")
            continue

        if len(coincidencias) > 40:
            print(f"  Hay {len(coincidencias)} coincidencias, son muchas. "
                  "Escribí algo más específico.")
            continue

        # Mostramos las coincidencias numeradas.
        print()
        for indice, usuario in enumerate(coincidencias, start=1):
            print(f"  {indice:3d}) {usuario}")

        seleccion = input("Elegí el número (Enter = buscar de nuevo): ").strip()
        if seleccion == "":
            continue
        if seleccion.isdigit() and 1 <= int(seleccion) <= len(coincidencias):
            return coincidencias[int(seleccion) - 1]
        print("  Número fuera de rango.")


def mostrar_tabla(registros, repositorio):
    """Imprime el seguimiento en una tabla simple en la consola."""
    if not registros:
        print("\n  No hay conexiones de ese usuario en ese rango de fechas.")
        return

    # Encabezado de la tabla.
    print("\n  {:<11} {:<9} {:<9} {:<10} {:>9} {:>12} {:>12}".format(
        "Fecha", "Inicio", "Fin", "Punto", "Dur.(s)", "Entrada(B)", "Salida(B)"))
    print("  " + "-" * 78)

    for r in registros:
        print("  {:<11} {:<9} {:<9} {:<10} {:>9} {:>12} {:>12}".format(
            r["inicio_dia"],
            r["inicio_hora"],
            r["fin_hora"],
            repositorio.etiqueta(r["mac_ap"]),
            r["session_time"],
            r["input_bytes"],
            r["output_bytes"],
        ))

    print("  " + "-" * 78)
    print(f"  Total de conexiones: {len(registros)}")

    # Resumen del recorrido: lista de puntos en el orden en que aparecieron.
    recorrido = []
    for r in registros:
        punto = repositorio.etiqueta(r["mac_ap"])
        if not recorrido or recorrido[-1] != punto:
            recorrido.append(punto)
    print("  Recorrido por el edificio: " + "  ->  ".join(recorrido))


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_estadisticas(repositorio, total_leidos):
    print("\n=== Estadísticas de la carga ===")
    print(f"  Registros leídos del CSV : {total_leidos:,}")
    print(f"  Registros válidos        : {len(repositorio.registros):,}")
    print(f"  Registros descartados    : {len(repositorio.descartados):,}")
    print(f"  Usuarios distintos       : {len(repositorio.usuarios()):,}")
    print(f"  Access Points distintos  : {len(repositorio.etiquetas_ap):,}")


def opcion_seguimiento(repositorio, validador, exportador):
    print("\n=== Seguimiento de usuario ===")
    usuario = elegir_usuario(repositorio)
    if usuario is None:
        print("  Cancelado.")
        return

    print(f"\n  Usuario elegido: {usuario}")
    print("  Ingresá el rango de fechas (para un solo día, poné la misma "
          "fecha en ambas).")
    desde = pedir_fecha(validador, "  Fecha desde (AAAA-MM-DD): ")
    hasta = pedir_fecha(validador, "  Fecha hasta (AAAA-MM-DD): ")

    if desde > hasta:
        desde, hasta = hasta, desde   # por si las ingresó al revés

    registros = repositorio.seguimiento(usuario, desde, hasta)
    mostrar_tabla(registros, repositorio)

    if registros:
        respuesta = input("\n  ¿Exportar a Excel? (s/n): ").strip().lower()
        if respuesta == "s":
            nombre = input("  Nombre del archivo (Enter = seguimiento.xlsx): ").strip()
            if nombre == "":
                nombre = "seguimiento.xlsx"
            if not nombre.endswith(".xlsx"):
                nombre += ".xlsx"
            exportador.exportar(registros, usuario, desde, hasta,
                                repositorio, nombre)
            print(f"  Listo. Archivo guardado: {os.path.abspath(nombre)}")


def opcion_descartados(repositorio, exportador):
    print("\n=== Registros descartados ===")
    if not repositorio.descartados:
        print("  No se descartó ningún registro.")
        return

    print(f"  Se descartaron {len(repositorio.descartados)} registros.")
    cantidad = input("  ¿Cuántos querés ver en pantalla? (Enter = 10): ").strip()
    cantidad = int(cantidad) if cantidad.isdigit() else 10

    for numero_linea, motivo, _fila in repositorio.descartados[:cantidad]:
        print(f"  Línea {numero_linea}: {motivo}")

    # Exportar TODOS los inválidos a Excel para poder analizarlos en detalle.
    respuesta = input(
        "\n  ¿Exportar TODOS los inválidos a Excel para analizarlos? (s/n): "
    ).strip().lower()
    if respuesta == "s":
        nombre = input("  Nombre del archivo (Enter = invalidos.xlsx): ").strip()
        if nombre == "":
            nombre = "invalidos.xlsx"
        if not nombre.endswith(".xlsx"):
            nombre += ".xlsx"
        exportador.exportar_invalidos(
            repositorio.descartados, repositorio.cabecera, nombre)
        print(f"  Listo. Archivo guardado: {os.path.abspath(nombre)}")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Seguimiento de conexiones WiFi - Trabajo Práctico Final")
    print("  Autómatas y Gramáticas")
    print("=" * 60)

    if not os.path.exists(ARCHIVO_CSV):
        print(f"\nERROR: no se encontró el archivo '{ARCHIVO_CSV}'.")
        print("Poné el CSV en la misma carpeta que este programa y volvé a "
              "ejecutarlo.")
        return

    # Armamos las piezas y cargamos los datos.
    validador = ValidadorRegistro()
    repositorio = RepositorioConexiones(validador)
    exportador = ExportadorExcel()

    print(f"\nLeyendo y validando '{ARCHIVO_CSV}' (puede tardar unos segundos)...")
    total_leidos = repositorio.cargar(ARCHIVO_CSV)
    print(f"Carga terminada: {len(repositorio.registros):,} válidos, "
          f"{len(repositorio.descartados):,} descartados.")

    # Bucle del menú.
    while True:
        print("\n----------------- MENÚ -----------------")
        print("  1) Ver estadísticas de la carga")
        print("  2) Hacer seguimiento de un usuario")
        print("  3) Ver registros descartados")
        print("  0) Salir")
        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            opcion_estadisticas(repositorio, total_leidos)
        elif opcion == "2":
            opcion_seguimiento(repositorio, validador, exportador)
        elif opcion == "3":
            opcion_descartados(repositorio, exportador)
        elif opcion == "0":
            print("\nHasta luego.")
            break
        else:
            print("  Opción inválida.")


if __name__ == "__main__":
    main()