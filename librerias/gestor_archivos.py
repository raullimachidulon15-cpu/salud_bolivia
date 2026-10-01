from pathlib import Path
import json
import re
import threading

BASE = Path(__file__).resolve().parent.parent
CARPETA_DATOS = BASE / "datos"
LOCK = threading.RLock()


# Crea la carpeta datos si no existe
def ruta(archivo):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    return CARPETA_DATOS / archivo


# Leer un archivo JSON
def leer_json(archivo):
    p = ruta(archivo)

    if not p.exists():
        return []

    with LOCK:
        try:
            with p.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []


# Guardar un archivo JSON
def guardar_json(archivo, datos):
    with LOCK:
        with ruta(archivo).open("w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)


# Agregar un registro a un archivo JSON
def agregar_json(archivo, registro):
    with LOCK:
        datos = leer_json(archivo)

        if not isinstance(datos, list):
            datos = []

        datos.append(registro)
        guardar_json(archivo, datos)


# Generar el siguiente ID
def siguiente_id(archivo, prefijo):
    maximo = 0

    datos = leer_json(archivo)

    for registro in datos:
        if not isinstance(registro, dict):
            continue

        # Busca el primer campo que contenga el ID
        identificador = (
            registro.get("id")
            or registro.get("id_cita")
            or registro.get("id_paciente")
            or registro.get("id_medico")
        )

        if not identificador:
            continue

        m = re.search(
            rf"^{re.escape(prefijo)}(\d+)$",
            str(identificador).strip()
        )

        if m:
            maximo = max(maximo, int(m.group(1)))

    return f"{prefijo}{maximo + 1:04d}"
def guardar_fila(archivo, fila):
    """Agrega una fila o registro a una lista JSON."""
    agregar_json(archivo, fila)