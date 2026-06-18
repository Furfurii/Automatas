# Seguimiento de conexiones WiFi — Trabajo Práctico Final
## Autómatas y Gramáticas

**Integrantes:** BARREDO VON JASTRZEMBSKI, Santiago Manuel — FURFURI, Franco — ZARZUR, Matias Andres

## ¿Qué hace el proyecto?

Sobre un archivo CSV con más de un millón de registros de tráfico WiFi, la aplicación permite hacer el **seguimiento de un usuario en un rango de fechas** para ver su desplazamiento por el edificio. Cada Access Point (`MAC_AP`) es un punto físico de la red, así que la secuencia de APs a los que se conectó un usuario es, en la práctica, su recorrido.

Antes de poder consultar, el programa **lee y valida** todos los registros con **expresiones regulares** (módulo `re`): guarda solo los que tienen todos los campos con formato correcto y no vacíos, y descarta el resto informando el motivo.

## Cómo ejecutarlo

**Requisitos:** Python 3.8 o superior.

**1.** Abrí una terminal en la carpeta del proyecto (en VS Code: `Ctrl+ñ`).

**2.** *(Recomendado)* Creá y activá un entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> Si PowerShell te bloquea la activación con un error de "execution policy", corré esto una sola vez y reintentá:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> Cuando el entorno está activo, vas a ver `(venv)` al principio de la línea.

**3.** Instalá las dependencias:

```powershell
pip install -r requirements.txt
```

**4.** Colocá el archivo `export-2019-to-now-v4.csv` en la **misma carpeta** que `main.py`. (No está en el repositorio por su tamaño; lo entregó la cátedra.)

**5.** Ejecutá el programa:

```powershell
python main.py
```

El programa tarda unos segundos en leer y validar el millón de registros al iniciar.

**6.** Usá el menú:
- **Opción 1** — ver estadísticas de la carga (válidos, descartados, usuarios, APs).
- **Opción 2** — hacer un seguimiento: buscás el usuario, ingresás el rango de fechas (para un solo día, la misma fecha en ambas) y, si querés, exportás el resultado a Excel.
- **Opción 3** — ver los registros descartados con su motivo.
- **Opción 0** — salir.

## Estructura del código

| Archivo | Clase | Qué hace |
|---|---|---|
| `validador.py` | `ValidadorRegistro` | Tiene las regex y decide si una fila es válida. Núcleo teórico de la materia. |
| `repositorio.py` | `RepositorioConexiones` | Lee el CSV, valida con el validador, guarda válidos (lista de diccionarios) y descartados, y ofrece las consultas. |
| `exportador.py` | `ExportadorExcel` | Vuelca el resultado de un seguimiento a un archivo `.xlsx`. |
| `main.py` | — | Interfaz de consola (menú) que conecta todo. |

## Cómo cumple la consigna

Implementado en **Python** con las herramientas de la materia · usa **expresiones regulares** y el módulo **`re`** · guarda los registros en una **lista de diccionarios** · guarda **solo los válidos** y muestra los descartados al final · **lista de usuarios** para filtrar y **rango de fechas** ingresable · muestra la info en la **interfaz** y **exporta a Excel**.