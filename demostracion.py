from librerias.gestor_archivos import (
    leer_json,
    guardar_json,
    agregar_json,
    siguiente_id,
)
from librerias.prosesador_texto import (
    clasificar_consulta,
    extraer_palabras_clave,
)
from librerias.buscador import (
    buscar_secuencial,
    ordenar_por,
    medir_tiempo,
)
from librerias.cola_prioridad import ColaPrioridad
from librerias.reubicacion import reubicar_pendientes


def preparar_datos():
    if not leer_json("medicos.json"):
        guardar_json(
            "medicos.json",
            [
                {
                    "id": "MED-0001",
                    "nombre": "Dra. Ana Pérez",
                    "especialidad": "Cardiología",
                    "turno": "Mañana",
                    "estado": "inactivo",
                },
                {
                    "id": "MED-0002",
                    "nombre": "Dr. Luis Mamani",
                    "especialidad": "Cardiología",
                    "turno": "Mañana",
                    "estado": "activo",
                },
            ],
        )

    if not leer_json("citas.json"):
        guardar_json(
            "citas.json",
            [
                {
                    "id_cita": "CITA-0001",
                    "id_paciente": "PAC-0001",
                    "id_medico": "MED-0001",
                    "nombre_medico": "Dra. Ana Pérez",
                    "especialidad": "Cardiología",
                    "turno": "Mañana",
                    "fecha": "2026-09-21",
                    "estado": "Pendiente de reubicacion",
                }
            ],
        )


def demostrar_gestor_y_procesador():
    consulta = "Tengo dolor de pecho y presión en el corazón."

    paciente = {
        "id_paciente": siguiente_id("pacientes.json", "PAC-"),
        "nombre": "María Quispe",
        "ci": "1234567",
        "consulta": consulta,
        "especialidades": clasificar_consulta(consulta),
        "palabras_clave": extraer_palabras_clave(consulta),
    }

    agregar_json("pacientes.json", paciente)

    print("\n1. Gestor de archivos + procesador de texto")
    print(paciente)

    return paciente


def demostrar_buscador():
    pacientes = leer_json("pacientes.json")

    encontrados, tiempo = medir_tiempo(
        buscar_secuencial,
        pacientes,
        "nombre",
        "maria",
    )

    print("\n2. Buscador")
    print("Resultados:", encontrados)
    print(f"Tiempo: {tiempo:.3f} ms")

    print("Pacientes ordenados:")
    print(ordenar_por(pacientes, "nombre"))


def demostrar_cola(paciente):
    cola = ColaPrioridad()

    cola.encolar(paciente, prioridad=1)
    cola.encolar(
        {"nombre": "Carlos Flores", "consulta": "Tengo tos"},
        prioridad=3,
    )

    print("\n3. Cola de prioridad")
    print("Siguiente paciente:", cola.desencolar())


def demostrar_reubicacion():
    cambios = reubicar_pendientes()

    print("\n4. Reubicación de citas")
    print(f"Citas reubicadas: {cambios}")
    print("Citas actuales:", leer_json("citas.json"))
    print("Notificaciones:", leer_json("notificaciones.json"))


if __name__ == "__main__":
    preparar_datos()
    paciente = demostrar_gestor_y_procesador()
    demostrar_buscador()
    demostrar_cola(paciente)
    demostrar_reubicacion()