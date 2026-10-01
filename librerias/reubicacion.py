from datetime import datetime, timedelta
from .gestor_archivos import (
    leer_json,
    guardar_json,
    agregar_json
)

ESTADOS_NO_ATENDIBLES = {"atendida", "cancelada"}

def siguiente_fecha_reubicacion():
    nueva_fecha = datetime.now() + timedelta(days=1)
    return nueva_fecha.strftime("%Y-%m-%d")

def buscar_reemplazo(lista_medicos, medico_id, especialidad, turno=None):
    for medico in lista_medicos:
        if medico.id == medico_id:
            continue
        if medico.estado.lower() != "activo":
            continue
        if medico.especialidad.lower() != especialidad.lower():
            continue
        if turno and medico.turno.lower() != turno.lower():
            continue
        return medico
    return None

def reprogramar_por_medico(
    medico_id,
    archivo_medicos="medicos.json",
    archivo_citas="citas.json",
    archivo_notificaciones="notificaciones.json",
):
    

    lista_medicos = ("medicos.join")

    medico_afectado = next(
        (
            medico
            for medico in lista_medicos
            if medico.id == medico_id
        ),
        None,
    )

    if not medico_afectado:
        return 0, []

    # Desactivar al médico en medicos.json
    registros_medicos = leer_json(archivo_medicos)

    for medico in registros_medicos:
        if not isinstance(medico, dict):
            continue

        if str(medico.get("id_medico",medico.get("id",""))) == str(medico_id):
            medico["estado"]="inactivo"
            break

    # Buscar y reprogramar sus citas
    citas = leer_json(archivo_citas)
    cambios = []

    for cita in citas:
        if not isinstance(cita, dict):
            continue

        if cita.get("id_medico") != medico_id:
            continue

        estado = cita.get("estado", "").strip().lower()

        if estado in ESTADOS_NO_ATENDIBLES:
            continue

        especialidad = cita.get("especialidad", "")
        turno = cita.get("turno", "")
        nueva_fecha = siguiente_fecha_reubicacion()

        reemplazo = buscar_reemplazo(
            lista_medicos,
            medico_id,
            especialidad,
            turno,
        )

        if reemplazo:
            cita["id_medico"] = reemplazo.id
            cita["nombre_medico"] = reemplazo.nombre
            cita["fecha"] = nueva_fecha
            cita["estado"] = "Reprogramada"

            mensaje = (
                f"Cita reprogramada con {reemplazo.nombre} "
                f"para {nueva_fecha}."
            )

            cambios.append(
                {
                    "id_cita": cita.get("id_cita", ""),
                    "medico": reemplazo.nombre,
                    "fecha": nueva_fecha,
                    "estado": "reprogramada",
                }
            )
        else:
            cita["id_medico"] = ""
            cita["nombre_medico"] = "Por asignar"
            cita["fecha"] = nueva_fecha
            cita["estado"] = "Pendiente de reubicacion"

            mensaje = "Médico no disponible. Cita pendiente de reubicación."

            cambios.append(
                {
                    "id_cita": cita.get("id_cita", ""),
                    "medico": "Por asignar",
                    "fecha": nueva_fecha,
                    "estado": "pendiente de reubicacion",
                }
            )

        agregar_json(
            archivo_notificaciones,
            {
                "id_cita": cita.get("id_cita", ""),
                "id_paciente": cita.get("id_paciente", ""),
                "mensaje": mensaje,
            },
        )

    guardar_json(archivo_medicos, registros_medicos)
    guardar_json(archivo_citas, citas)

    agregar_json(
        archivo_notificaciones,
        {
            "tipo": "medico_desactivado",
            "id_medico": medico_id,
            "mensaje": (
                f"{medico_afectado.nombre} marcado como no disponible. "
                f"Citas afectadas: {len(cambios)}."
            ),
        },
    )

    return len(cambios), cambios

def reactivar_medico(
    medico_id,
    archivo_medicos="medicos.json",
):
    registros_medicos = leer_json(archivo_medicos)

    if not isinstance(registros_medicos, list):
        return False

    for medico in registros_medicos:
        if not isinstance(medico, dict):
            continue

        id_guardado = medico.get("id") or medico.get("id_medico")

        if str(id_guardado) == str(medico_id):
            medico["estado"] = "activo"
            guardar_json(archivo_medicos, registros_medicos)
            return True

    return False

def buscar_reemplazo_json(medicos, medico_id, especialidad, turno):
    for medico in medicos:
        if not isinstance(medico, dict):
            continue

        id_medico = medico.get("id") or medico.get("id_medico")

        if str(id_medico) == str(medico_id):
            continue

        if medico.get("estado", "").lower() != "activo":
            continue

        if medico.get("especialidad", "").lower() != especialidad.lower():
            continue

        if medico.get("turno", "").lower() != turno.lower():
            continue

        return medico

    return None


def reubicar_pendientes(
    archivo_medicos="medicos.json",
    archivo_citas="citas.json",
    archivo_notificaciones="notificaciones.json",
):
    medicos = leer_json(archivo_medicos)
    citas = leer_json(archivo_citas)
    notificaciones = leer_json(archivo_notificaciones)
    if not isinstance(medicos, list):
        medicos = []
    if not isinstance(citas, list):
        citas = []
    if not isinstance(notificaciones, list):
        notificaciones = []
    cambios = 0

    for cita in citas:
        if not isinstance(cita, dict):
            continue

        if cita.get("estado", "").strip().lower() not in {"pendiente de reubicacion", "pendiente de reubicación"}:
            continue

        reemplazo = buscar_reemplazo_json(
            medicos,
            cita.get("id_medico", ""),
            cita.get("especialidad", ""),
            cita.get("turno", ""),
        )

        if not reemplazo:
            continue

        nueva_fecha = siguiente_fecha_reubicacion()

        cita["id_medico"] = reemplazo.get("id", "")
        cita["nombre_medico"] = reemplazo.get("nombre", "")
        cita["fecha"] = nueva_fecha
        cita["estado"] = "Reprogramada"

        notificaciones.append({
                "id_cita": cita.get("id_cita", ""),
                "mensaje": (
                    f"Cita reubicada con "
                    f"{reemplazo.get('nombre', '')} "
                    f"para {nueva_fecha}."
                ),
            })

        cambios += 1

    guardar_json(archivo_citas, citas)
    guardar_json(archivo_notificaciones, notificaciones)
    return cambios
