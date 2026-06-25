"""
Consolida todos los CSV de colaboradores (datos/heridos_*.csv) en un único
Excel y CSV maestro, eliminando duplicados globalmente.

Uso:
    python consolidar.py

Genera:
    heridos_consolidado.xlsx
    heridos_consolidado.csv

Regla anti-duplicados (igual que la app):
  - Clave = cédula real, o TEMP_NOMBRE_APELLIDO_EDAD si no hay cédula.
  - Si la misma persona aparece en varios CSV, se conserva el registro
    con MÁS campos completos (menos "SIN DATOS").

Este script NO necesita GEMINI_API_KEY: solo lee archivos locales.
"""

import os
import re
import csv
import glob

from openpyxl import Workbook

DATA_DIR = "datos"
HEADERS = ["cedula_id", "nombre", "apellido", "edad", "ubicacion"]
OUT_XLSX = "heridos_consolidado.xlsx"
OUT_CSV = "heridos_consolidado.csv"


def normalize(value):
    if value is None:
        return "SIN DATOS"
    s = str(value).strip()
    return s if s else "SIN DATOS"


def build_key(p):
    cedula = normalize(p.get("cedula_id")).upper()
    if cedula and cedula != "SIN DATOS":
        return re.sub(r"\s+", "", cedula)
    raw = f"TEMP_{normalize(p.get('nombre'))}_{normalize(p.get('apellido'))}_{normalize(p.get('edad'))}"
    return re.sub(r"\s+", "", raw).upper()


def completeness(p):
    """Cuántos campos tienen datos reales (no 'SIN DATOS')."""
    return sum(1 for h in HEADERS if normalize(p.get(h)) != "SIN DATOS")


def main():
    archivos = sorted(glob.glob(os.path.join(DATA_DIR, "heridos_*.csv")))
    if not archivos:
        print(f"No se encontraron CSV en '{DATA_DIR}/'. Genero un consolidado vacío.")

    consolidado = {}   # clave -> {fila..., "fuente": colaborador}
    total_leidos = 0

    for ruta in archivos:
        colaborador = os.path.basename(ruta).replace("heridos_", "").replace(".csv", "")
        try:
            with open(ruta, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    fila = {h: normalize(r.get(h)) for h in HEADERS}
                    total_leidos += 1
                    key = build_key(fila)
                    fila["fuente"] = colaborador
                    actual = consolidado.get(key)
                    # Conserva el registro más completo; en empate, el ya existente.
                    if actual is None or completeness(fila) > completeness(actual):
                        consolidado[key] = fila
        except Exception as e:  # noqa: BLE001
            print(f"  AVISO: no se pudo leer {ruta}: {e}")

    filas = list(consolidado.values())
    # Orden estable: por ubicación y luego apellido.
    filas.sort(key=lambda p: (p["ubicacion"].lower(), p["apellido"].lower()))

    columnas = HEADERS + ["fuente"]

    # --- Excel ---
    wb = Workbook()
    ws = wb.active
    ws.title = "Consolidado"
    ws.append(columnas)
    for p in filas:
        ws.append([p.get(c, "") for c in columnas])
    wb.save(OUT_XLSX)

    # --- CSV maestro ---
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for p in filas:
            writer.writerow({c: p.get(c, "") for c in columnas})

    print(f"Colaboradores: {len(archivos)}  |  Registros leídos: {total_leidos}")
    print(f"Pacientes únicos tras dedup: {len(filas)}")
    print(f"Generado: {OUT_XLSX} y {OUT_CSV}")


if __name__ == "__main__":
    main()
