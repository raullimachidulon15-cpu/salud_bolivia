# Agenda Médica Salud Bolivia

Aplicación web sencilla para registrar pacientes y reservar, buscar, priorizar, cancelar y reubicar citas. Los datos de demostración se guardan en archivos JSON dentro de `datos/`.

El formulario permite dictar el motivo de consulta desde el micrófono del equipo donde corre Django; también se puede buscar una cita hablando. El texto reconocido pasa por las librerías Python propias de la agenda. La descarga de citas se ofrece como XML, con DTD incluido.

## Ejecutar

Requiere Python, Django, un micrófono conectado y acceso a internet para el servicio de transcripción. Desde esta carpeta ejecuta:

```powershell
python -m pip install -r requirements.txt
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador. Los médicos se administran en `datos/medicos.json`; registra médicos con `estado` igual a `activo` para que aparezcan al reservar.

## Librerías propias usadas

- `gestor_archivos.py`: lectura y escritura JSON e identificadores.
- `buscador.py`: búsqueda de citas por paciente y orden de registros.
- `cola_prioridad.py`: muestra la siguiente cita según prioridad.
- `prosesador_texto.py`: obtiene palabras clave y sugiere especialidades según el motivo escrito.
- `reubicacion.py`: busca un médico de reemplazo para citas pendientes.

Los ejemplos de OpenCV, OpenGL y NumPy se conservan como material de clase porque no hacen falta en el flujo de agenda. El XML se usa para exportar las citas; los archivos JSON continúan siendo el almacenamiento principal.

La voz se captura mediante la librería Python `SpeechRecognition` y PyAudio. Por eso Django debe ejecutarse localmente en el equipo conectado al micrófono; el texto reconocido se revisa antes de confirmar la cita. La búsqueda hablada reconoce un nombre y lo pasa al buscador propio. `recognize_google` requiere internet y envía el audio al servicio de reconocimiento de Google; el audio no se guarda en los archivos del proyecto.

## Alcance

Es una demostración local para clases; no está preparada para publicar en internet ni para almacenar datos médicos reales. La sugerencia de especialidad es orientativa y no diagnostica.
