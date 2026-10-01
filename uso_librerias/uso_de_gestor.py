from pathlib import Path
import json
import re
import threading


BASE = Path(__file__).resolve().parent.parent
CARPETA_DATOS = BASE / "datos"
LOCK = threading.RLock()


def ruta(archivo):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    return CARPETA_DATOS / archivo


def leer_json(archivo):
    archivo_ruta = ruta(archivo)

    if not archivo_ruta.exists() or archivo_ruta.stat().st_size == 0:
        return []

    with LOCK:
        try:
            with archivo_ruta.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []


def guardar_json(archivo, datos):
    with LOCK:
        with ruta(archivo).open("w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)


def agregar_json(archivo, registro):
    datos = leer_json(archivo)

    if not isinstance(datos, list):
        datos = []

    datos.append(registro)
    guardar_json(archivo, datos)


def siguiente_id(archivo, prefijo):
    maximo = 0

    for registro in leer_json(archivo):
        if not isinstance(registro, dict):
            continue

        identificador = (
            registro.get("id")
            or registro.get("id_paciente")
            or registro.get("id_medico")
            or registro.get("id_cita")
        )

        coincidencia = re.search(
            rf"^{re.escape(prefijo)}(\d+)$",
            str(identificador or ""),
        )

        if coincidencia:
            maximo = max(maximo, int(coincidencia.group(1)))

    return f"{prefijo}{maximo + 1:04d}"