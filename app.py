"""
Sistema de triaje de emergencia: OCR de listas de heridos -> CSV por colaborador.

Flujo:
  1. El usuario sube una captura/foto de una lista física de heridos.
  2. Gemini extrae los pacientes en JSON estructurado.
  3. Se vuelcan a un CSV propio del colaborador (datos/heridos_<colaborador>.csv),
     evitando duplicados dentro de ese archivo.
  4. Cada colaborador commitea SOLO su CSV -> nunca hay conflictos de git.
  5. 'consolidar.py' junta todos los CSV en heridos_consolidado.xlsx sin duplicados.

Variables de entorno:
  GEMINI_API_KEY  -> clave de la API de Gemini (la usa genai.Client() automáticamente).
  COLABORADOR     -> tu nombre/identificador (define el nombre de tu archivo de datos).
                     Ej: export COLABORADOR="ricardo"
"""

import os
import re
import csv
import json
import logging
import threading

from flask import Flask, render_template, request, jsonify, send_file

# --- SDK de Gemini (nuevo, oficial) ---
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# CONFIGURACIÓN  (AJUSTAR AQUÍ)
# ---------------------------------------------------------------------------
DATA_DIR = "datos"                                   # Carpeta con un CSV por colaborador
COLABORADOR = os.environ.get("COLABORADOR", "anonimo")  # Tu identificador
GEMINI_MODEL = "gemini-2.5-flash"

# Columnas, en orden. La cédula se usa como clave anti-duplicados.
HEADERS = ["cedula_id", "nombre", "apellido", "edad", "ubicacion"]

# ---------------------------------------------------------------------------
# INICIALIZACIÓN
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("triaje")

app = Flask(__name__)

# Lock para evitar que dos subidas simultáneas corrompan el CSV.
_csv_lock = threading.Lock()

# Cliente de Gemini. Lee GEMINI_API_KEY del entorno automáticamente.
try:
    gemini_client = genai.Client()
    log.info("Cliente Gemini inicializado.")
except Exception as e:  # noqa: BLE001
    gemini_client = None
    log.error("No se pudo inicializar Gemini. Revisa GEMINI_API_KEY. Detalle: %s", e)


# ---------------------------------------------------------------------------
# PROMPT DE EXTRACCIÓN
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """Actúa en MODO DE EMERGENCIA HUMANITARIA tras un terremoto.
Estás procesando la foto/captura de una lista física de personas heridas.
Tu única tarea es extraer TODOS los pacientes legibles de la imagen.

Devuelve EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional, con esta forma exacta:
{
  "pacientes": [
    {"nombre": "...", "apellido": "...", "edad": "...", "cedula_id": "...", "ubicacion": "..."}
  ]
}

Reglas estrictas:
- Si un campo (cédula, edad, etc.) no aparece o es ilegible, usa el texto "SIN DATOS".
- NO inventes datos. Si dudas, marca "SIN DATOS".
- "edad" debe ser solo el número si está disponible.
- "cedula_id" es el documento de identidad / cédula.
- Si la imagen no contiene ninguna persona legible, devuelve {"pacientes": []}.
"""


# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------
def normalize(value):
    """Normaliza un valor a string limpio; vacío -> 'SIN DATOS'."""
    if value is None:
        return "SIN DATOS"
    s = str(value).strip()
    return s if s else "SIN DATOS"


def slug(texto):
    """Convierte un nombre en un identificador seguro para nombre de archivo."""
    s = re.sub(r"[^a-z0-9]+", "_", str(texto).strip().lower())
    return s.strip("_") or "anonimo"


def build_key(paciente):
    """
    Clave anti-duplicados.
    - Si hay cédula real -> se usa la cédula (mayúsculas, sin espacios).
    - Si la cédula es 'SIN DATOS'/vacía -> TEMP_NOMBRE_APELLIDO_EDAD.
    """
    cedula = normalize(paciente.get("cedula_id")).upper()
    if cedula and cedula != "SIN DATOS":
        return re.sub(r"\s+", "", cedula)

    nombre = normalize(paciente.get("nombre"))
    apellido = normalize(paciente.get("apellido"))
    edad = normalize(paciente.get("edad"))
    raw = f"TEMP_{nombre}_{apellido}_{edad}"
    return re.sub(r"\s+", "", raw).upper()


def data_file():
    """Ruta del CSV de este colaborador. Crea la carpeta 'datos/' si no existe."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"heridos_{slug(COLABORADOR)}.csv")


# ---------------------------------------------------------------------------
# OCR CON GEMINI
# ---------------------------------------------------------------------------
def extract_patients(image_bytes, mime_type, ubicacion_defecto):
    """Llama a Gemini y devuelve una lista de pacientes normalizados."""
    if gemini_client is None:
        raise RuntimeError("Cliente Gemini no disponible. Revisa GEMINI_API_KEY.")

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            EXTRACTION_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )

    raw_text = (response.text or "").strip()
    if not raw_text:
        raise ValueError("Gemini devolvió una respuesta vacía.")

    # Robustez extra: por si el modelo envuelve el JSON en ```json ... ```
    raw_text = re.sub(r"^```(?:json)?|```$", "", raw_text, flags=re.MULTILINE).strip()

    data = json.loads(raw_text)
    pacientes_raw = data.get("pacientes", [])

    pacientes = []
    for p in pacientes_raw:
        ubicacion = normalize(p.get("ubicacion"))
        if ubicacion == "SIN DATOS" and ubicacion_defecto:
            ubicacion = ubicacion_defecto
        pacientes.append(
            {
                "cedula_id": normalize(p.get("cedula_id")),
                "nombre": normalize(p.get("nombre")),
                "apellido": normalize(p.get("apellido")),
                "edad": normalize(p.get("edad")),
                "ubicacion": ubicacion,
            }
        )
    return pacientes


# ---------------------------------------------------------------------------
# CSV LOCAL (uno por colaborador)
# ---------------------------------------------------------------------------
def read_rows(path):
    """Lee el CSV del colaborador y devuelve una lista de dicts normalizados."""
    rows = []
    if os.path.exists(path):
        # utf-8-sig para que Excel abra los acentos correctamente.
        with open(path, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows.append({h: normalize(r.get(h)) for h in HEADERS})
    return rows


def write_rows(path, rows):
    """Reescribe el CSV completo del colaborador."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow({h: r.get(h, "") for h in HEADERS})


def sync_to_csv(pacientes):
    """
    Inserta o actualiza pacientes en el CSV del colaborador.
    Devuelve (insertados, actualizados).
    """
    with _csv_lock:
        path = data_file()
        rows = read_rows(path)
        index = {build_key(r): i for i, r in enumerate(rows)}

        insertados = 0
        actualizados = 0

        for p in pacientes:
            key = build_key(p)
            row = {h: p[h] for h in HEADERS}
            if key in index:
                rows[index[key]] = row
                actualizados += 1
            else:
                index[key] = len(rows)
                rows.append(row)
                insertados += 1

        write_rows(path, rows)

    return insertados, actualizados


# ---------------------------------------------------------------------------
# RUTAS
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", colaborador=COLABORADOR)


@app.route("/procesar", methods=["POST"])
def procesar():
    try:
        if "imagen" not in request.files or request.files["imagen"].filename == "":
            return jsonify({"ok": False, "error": "No se recibió ninguna imagen."}), 400

        archivo = request.files["imagen"]
        ubicacion_defecto = (request.form.get("ubicacion") or "").strip()

        image_bytes = archivo.read()
        mime_type = archivo.mimetype or "image/jpeg"

        # 1) OCR con Gemini
        try:
            pacientes = extract_patients(image_bytes, mime_type, ubicacion_defecto)
        except json.JSONDecodeError:
            return jsonify(
                {"ok": False, "error": "Gemini no devolvió un JSON válido. Reintenta con mejor foto."}
            ), 502
        except Exception as e:  # noqa: BLE001
            log.exception("Error en extracción Gemini")
            return jsonify({"ok": False, "error": f"Error de OCR/Gemini: {e}"}), 502

        if not pacientes:
            return jsonify(
                {"ok": True, "pacientes": [], "insertados": 0, "actualizados": 0,
                 "mensaje": "No se detectaron pacientes legibles en la imagen."}
            )

        # 2) Volcado al CSV del colaborador
        try:
            insertados, actualizados = sync_to_csv(pacientes)
        except Exception as e:  # noqa: BLE001
            log.exception("Error guardando en CSV")
            return jsonify(
                {"ok": False, "error": f"Pacientes extraídos pero falló el guardado: {e}",
                 "pacientes": pacientes}
            ), 500

        return jsonify(
            {
                "ok": True,
                "pacientes": pacientes,
                "insertados": insertados,
                "actualizados": actualizados,
                "mensaje": f"{insertados} nuevos, {actualizados} actualizados.",
            }
        )

    except Exception as e:  # noqa: BLE001
        log.exception("Error inesperado")
        return jsonify({"ok": False, "error": f"Error inesperado: {e}"}), 500


@app.route("/descargar")
def descargar():
    """Descarga el CSV propio de este colaborador."""
    path = data_file()
    if not os.path.exists(path):
        return "Aún no hay datos. Procesa al menos una imagen.", 404
    return send_file(
        os.path.abspath(path),
        as_attachment=True,
        download_name=os.path.basename(path),
        mimetype="text/csv",
    )


if __name__ == "__main__":
    log.info("Colaborador: %s  ->  %s", COLABORADOR, data_file())
    # host 0.0.0.0 para que sea accesible desde móviles en la misma red.
    app.run(host="0.0.0.0", port=5000, debug=False)
