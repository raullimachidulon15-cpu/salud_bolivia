from datetime import date
import re
from xml.etree.ElementTree import Element, SubElement, tostring

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from librerias.buscador import buscar_secuencial, medir_tiempo, ordenar_por
from librerias.cola_prioridad import ColaPrioridad
from librerias.gestor_archivos import agregar_json, guardar_json, leer_json, siguiente_id
from librerias.prosesador_texto import clasificar_consulta, extraer_palabras_clave
from librerias.reubicacion import reubicar_pendientes


def _lista(valor):
    return valor if isinstance(valor, list) else []


def _siguiente_en_cola(citas):
    cola = ColaPrioridad()
    for cita in citas:
        if isinstance(cita, dict) and cita.get("estado") in {"Programada", "En espera"}:
            cola.encolar(cita, int(cita.get("prioridad", 3)))
    return cola.desencolar()


def _escuchar_y_transcribir():
    try:
        import speech_recognition as sr
    except ImportError as error:
        raise RuntimeError("Falta instalar SpeechRecognition y PyAudio para usar el micrófono.") from error

    try:
        reconocedor = sr.Recognizer()
        with sr.Microphone() as microfono:
            reconocedor.adjust_for_ambient_noise(microfono, duration=0.4)
            audio = reconocedor.listen(microfono, timeout=6, phrase_time_limit=12)
        return reconocedor.recognize_google(audio, language="es-BO").strip()
    except sr.WaitTimeoutError as error:
        raise RuntimeError("No se detectó voz. Pulsa el botón y habla cerca del micrófono.") from error
    except sr.UnknownValueError as error:
        raise RuntimeError("No se pudo entender la voz. Inténtalo de nuevo.") from error
    except sr.RequestError as error:
        raise RuntimeError("No se pudo conectar con el servicio de transcripción.") from error
    except (OSError, AttributeError) as error:
        raise RuntimeError("No se pudo abrir el micrófono. Revisa PyAudio y el dispositivo de audio.") from error


def inicio(request):
    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion in {"dictar_consulta", "buscar_voz"}:
            try:
                if accion == "dictar_consulta":
                    request.session["borrador_cita"] = {
                        campo: request.POST.get(campo, "")
                        for campo in ("nombre", "ci", "medico", "fecha", "hora", "prioridad")
                    }
                texto = _escuchar_y_transcribir()
                if not texto:
                    raise RuntimeError("No se recibió texto de la transcripción.")
                if accion == "dictar_consulta":
                    request.session["consulta_dictada"] = texto
                    messages.success(request, "Voz convertida a texto. Revisa el motivo y completa los datos para confirmar la cita.")
                else:
                    texto = re.sub(r"^(?:quiero\s+)?(?:buscar|busca|encuentra|mostrar|muestrame)(?:\s+(?:por\s+voz|(?:la\s+)?(?:cita|citas|paciente|pacientes)|a|al|de|del))*\s*", "", texto, flags=re.IGNORECASE).strip()
                    request.session["busqueda_dictada"] = texto
                    messages.success(request, f"Búsqueda por voz: {texto or 'mostrando todas las citas'}.")
            except RuntimeError as error:
                messages.error(request, str(error))
            return redirect("inicio")

        if accion == "reservar":
            nombre = request.POST.get("nombre", "").strip()
            ci = request.POST.get("ci", "").strip()
            consulta = request.POST.get("consulta", "").strip()
            medico_id = request.POST.get("medico", "").strip()
            fecha = request.POST.get("fecha", "").strip()
            hora = request.POST.get("hora", "").strip()
            try:
                prioridad = int(request.POST.get("prioridad", "3"))
            except ValueError:
                prioridad = 3
            request.session["borrador_cita"] = {
                "nombre": nombre, "ci": ci, "medico": medico_id,
                "fecha": fecha, "hora": hora, "prioridad": str(prioridad),
            }

            medicos = _lista(leer_json("medicos.json"))
            medico = next((m for m in medicos if isinstance(m, dict) and m.get("id", m.get("id_medico")) == medico_id), None)
            citas = _lista(leer_json("citas.json"))
            errores = []
            if not nombre or not ci or not consulta or not fecha or not hora:
                errores.append("Completa todos los datos del paciente y de la cita.")
            try:
                fecha_obj = date.fromisoformat(fecha)
                if fecha_obj < date.today():
                    errores.append("La fecha de la cita debe ser hoy o una fecha futura.")
            except ValueError:
                errores.append("Selecciona una fecha válida.")
            if prioridad not in (1, 2, 3):
                errores.append("Selecciona una prioridad válida.")
            if not medico or medico.get("estado", "").lower() != "activo":
                errores.append("Selecciona un médico activo.")
            if any(c.get("id_medico") == medico_id and c.get("fecha") == fecha and c.get("hora") == hora and c.get("estado") not in {"Cancelada", "Atendida"} for c in citas if isinstance(c, dict)):
                errores.append("Ese horario ya está ocupado. Elige otra hora.")

            if errores:
                for error in errores:
                    messages.error(request, error)
            else:
                pacientes = _lista(leer_json("pacientes.json"))
                paciente = next((p for p in pacientes if isinstance(p, dict) and p.get("ci") == ci), None)
                if paciente is None:
                    paciente = {
                        "id_paciente": siguiente_id("pacientes.json", "PAC-"),
                        "nombre": nombre,
                        "ci": ci,
                        "consulta": consulta,
                        "especialidades": clasificar_consulta(consulta),
                        "palabras_clave": extraer_palabras_clave(consulta),
                    }
                    agregar_json("pacientes.json", paciente)
                especialidades = clasificar_consulta(consulta)
                cita = {
                    "id_cita": siguiente_id("citas.json", "CITA-"),
                    "id_paciente": paciente["id_paciente"],
                    "nombre_paciente": nombre,
                    "ci": ci,
                    "consulta": consulta,
                    "id_medico": medico.get("id", medico.get("id_medico", "")),
                    "nombre_medico": medico.get("nombre", ""),
                    "especialidad": medico.get("especialidad", "Medicina General"),
                    "especialidades_sugeridas": especialidades,
                    "palabras_clave": extraer_palabras_clave(consulta),
                    "fecha": fecha,
                    "hora": hora,
                    "prioridad": prioridad,
                    "estado": "Programada",
                }
                agregar_json("citas.json", cita)
                request.session.pop("consulta_dictada", None)
                request.session.pop("borrador_cita", None)
                messages.success(request, f"Cita {cita['id_cita']} reservada para {nombre}.")

        elif accion == "cancelar":
            cita_id = request.POST.get("cita_id", "")
            citas = _lista(leer_json("citas.json"))
            encontrada = next((c for c in citas if isinstance(c, dict) and c.get("id_cita") == cita_id), None)
            if encontrada and encontrada.get("estado") not in {"Cancelada", "Atendida"}:
                encontrada["estado"] = "Cancelada"
                guardar_json("citas.json", citas)
                messages.success(request, f"La cita {cita_id} fue cancelada.")
            else:
                messages.error(request, "No se encontró una cita que se pueda cancelar.")

        elif accion == "reubicar":
            cantidad = reubicar_pendientes()
            messages.success(request, f"Citas reubicadas: {cantidad}.")

        return redirect("inicio")

    pacientes = _lista(leer_json("pacientes.json"))
    citas = _lista(leer_json("citas.json"))
    texto_busqueda = request.GET.get("q", request.session.pop("busqueda_dictada", "")).strip()
    resultados = citas
    tiempo_busqueda = None
    if texto_busqueda:
        resultados, tiempo_busqueda = medir_tiempo(buscar_secuencial, citas, "nombre_paciente", texto_busqueda)

    return render(request, "dashboard/inicio.html", {
        "pacientes": ordenar_por(pacientes, "nombre"),
        "cantidad_pacientes": len(pacientes),
        "siguiente": _siguiente_en_cola(citas),
        "citas": sorted(resultados, key=lambda c: (c.get("fecha", ""), c.get("hora", ""))),
        "cantidad_citas": len(citas),
        "medicos": ordenar_por([m for m in _lista(leer_json("medicos.json")) if isinstance(m, dict) and m.get("estado") == "activo"], "nombre"),
        "notificaciones": _lista(leer_json("notificaciones.json"))[-5:][::-1],
        "q": texto_busqueda,
        "tiempo_busqueda": tiempo_busqueda,
        "hoy": date.today().isoformat(),
        "consulta_dictada": request.session.get("consulta_dictada", ""),
        "borrador_cita": request.session.get("borrador_cita", {}),
    })


def exportar_citas_xml(request):
    raiz = Element("citas")
    campos = ("id_cita", "id_paciente", "nombre_paciente", "ci", "consulta", "id_medico", "nombre_medico", "especialidad", "fecha", "hora", "prioridad", "estado")
    for cita in _lista(leer_json("citas.json")):
        if not isinstance(cita, dict):
            continue
        nodo = SubElement(raiz, "cita")
        for campo in campos:
            SubElement(nodo, campo).text = str(cita.get(campo, ""))
    campos_dtd = ", ".join(campos)
    declaraciones = "\n".join(f"<!ELEMENT {campo} (#PCDATA)>" for campo in campos)
    doctype = f"<!DOCTYPE citas [\n<!ELEMENT citas (cita*)>\n<!ELEMENT cita ({campos_dtd})>\n{declaraciones}\n]>\n"
    contenido = b'<?xml version="1.0" encoding="UTF-8"?>\n' + doctype.encode("utf-8") + tostring(raiz, encoding="utf-8")
    respuesta = HttpResponse(contenido, content_type="application/xml; charset=utf-8")
    respuesta["Content-Disposition"] = 'attachment; filename="citas.xml"'
    return respuesta
