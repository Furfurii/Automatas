# Seguimiento de conexiones WiFi — Trabajo Práctico Final
## Autómatas y Gramáticas

**Integrantes:** BARREDO VON JASTRZEMBSKI, Santiago Manuel — FURFURI, Franco — ZARZUR, Matias Andres

---

## ¿Qué hace el proyecto?

Sobre un archivo CSV con más de un millón de registros de tráfico WiFi (conexiones
de distintos usuarios y dispositivos a una red), la aplicación permite hacer el
**seguimiento de un usuario en un rango de fechas** para ver su desplazamiento por
el edificio. Cada Access Point (campo `MAC_AP`) es un punto físico de la red, así
que la secuencia de APs a los que se conectó un usuario es, en la práctica, su
recorrido por el edificio.

Antes de poder consultar nada, el programa **lee y valida** todos los registros con
**expresiones regulares** (módulo `re`): guarda solo los que tienen todos los campos
con formato correcto y no vacíos, y descarta el resto informando el motivo.

## ¿Para qué sirve la información?

- Reconstruir por dónde se movió una persona dentro del edificio en un día o período.
- Detectar en qué zonas (APs) pasó más tiempo o transfirió más datos.
- Auditar el uso de la red por usuario.

---

## Cómo ejecutarlo

1. Necesitás **Python 3** y la librería **openpyxl** (para exportar a Excel):
   ```
   pip install openpyxl
   ```
2. Poné el archivo `export-2019-to-now-v4.csv` en la **misma carpeta** que los `.py`.
3. Ejecutá:
   ```
   python main.py
   ```
4. Usá el menú: ver estadísticas, hacer un seguimiento (elegís usuario + rango de
   fechas y, si querés, exportás a Excel) o ver los registros descartados.

---

## Estructura del código (4 archivos, una responsabilidad cada uno)

| Archivo | Clase | Qué hace |
|---|---|---|
| `validador.py` | `ValidadorRegistro` | Tiene las regex y decide si una fila es válida. **Es el núcleo teórico de la materia.** |
| `repositorio.py` | `RepositorioConexiones` | Lee el CSV, valida cada fila con el validador, guarda los válidos (lista de diccionarios) y los descartados, y ofrece las consultas. |
| `exportador.py` | `ExportadorExcel` | Vuelca el resultado de un seguimiento a un archivo `.xlsx`. |
| `main.py` | — | Interfaz de consola (menú) que conecta todo. |

Cada clase no sabe nada de las otras más allá de lo necesario (por ejemplo, el
repositorio solo le *pregunta* al validador si una fila es válida, sin saber cómo
lo decide). Esto es la idea de **responsabilidad única** de POO.

---

## Las expresiones regulares usadas (módulo `re`)

| Campo | Significado | Expresión regular |
|---|---|---|
| Fecha | año-mes-día | `\d{4}-\d{2}-\d{2}` |
| Hora | hh:mm:ss | `\d{2}:\d{2}:\d{2}` |
| Session_Time / Octets | entero no negativo | `\d+` |
| MAC_AP | 6 pares hex + `:HCDD` | `([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}:HCDD` |
| MAC_Cliente | 6 pares hex | `([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}` |
| Usuario | alfanumérico + `. - _` | `[\w.\-]+` |
| Tipo de conexión | texto fijo | `Wireless-802\.11` |

Se validan con `.fullmatch()`, que exige que **toda** la cadena cumpla el patrón.

> **Idea para defender en el oral:** validar un campo con una regex es preguntar si
> la cadena pertenece al lenguaje regular que describe esa expresión. Eso es,
> exactamente, lo que hace un autómata finito: leer la cadena y decidir ACEPTA o
> RECHAZA.

---

## Cómo cumple cada punto de la consigna

- ✅ Implementado en **Python** con las herramientas de la materia.
- ✅ Usa **expresiones regulares** y el **módulo `re`**.
- ✅ Guarda los registros leídos en una **lista de diccionarios**.
- ✅ Guarda **solo los válidos**; descarta los que tienen errores y los **muestra al final**.
- ✅ **Lista de usuarios** para filtrar y **rango de fechas** ingresable.
- ✅ Muestra la información en la **interfaz** y **exporta a Excel**.
