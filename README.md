# 🆘 Triaje de Emergencia — OCR de listas de heridos

Sistema web ligero para **digitalizar listas de heridos** a partir de fotos/capturas,
usando IA (Google Gemini) para el OCR. Pensado para usarse **desde el móvil en terreno**
durante una emergencia (ej. terremoto).

Cada colaborador procesa fotos en su propio teléfono/PC y los datos se guardan en **su
propio archivo CSV**. Luego un coordinador los **consolida** en un único Excel sin
duplicados. Este diseño evita por completo los conflictos de Git.

---

## ⚠️ Disclaimer / Aviso importante

> **Los datos de este repositorio provienen de capturas de pantalla de redes sociales y
> fueron extraídos automáticamente mediante inteligencia artificial (OCR con Google
> Gemini).**
>
> En consecuencia:
> - La información **puede contener errores, omisiones o imprecisiones** (nombres mal
>   leídos, cédulas incompletas, edades equivocadas, duplicados no detectados, etc.).
> - **NO es una fuente oficial** ni un registro médico o gubernamental verificado.
> - Debe **contrastarse con fuentes confirmadas** antes de usarse para localizar personas,
>   tomar decisiones médicas, logísticas o de cualquier tipo crítico.
> - Se publica con fines de **apoyo humanitario y coordinación de emergencia**, sin
>   garantía de exactitud ni completitud.
>
> Al usar o contribuir a este proyecto, entiendes y aceptas estas limitaciones. Trata los
> datos de personas con la **confidencialidad y el cuidado** que merecen.

---

## 📑 Tabla de contenido
- [Cómo funciona (resumen)](#-cómo-funciona-resumen)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración (API key + nombre)](#-configuración)
- [Uso diario](#-uso-diario)
- [Acceso desde el móvil](#-acceso-desde-el-móvil)
- [Reglas para colaborar en GitHub](#-reglas-para-colaborar-en-github-importante)
- [Consolidar el Excel final](#-consolidar-el-excel-final)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Problemas comunes](#-problemas-comunes)
- [Seguridad](#-seguridad)

---

## 🔎 Cómo funciona (resumen)

```
 Foto de la lista  ──►  Gemini (OCR)  ──►  datos/heridos_TUNOMBRE.csv  (commit tuyo)
                                                      │
              (varios colaboradores, cada uno su CSV) │
                                                      ▼
                              python consolidar.py  ──►  heridos_consolidado.xlsx
```

- **Anti-duplicados:** la cédula es la clave única. Si una persona no tiene cédula
  legible, se usa `TEMP_NOMBRE_APELLIDO_EDAD`. Reprocesar la misma foto **no duplica**.
- Cada colaborador trabaja en **su propio archivo** → nunca chocan en Git.

---

## 📦 Requisitos

- **Python 3.10+**
- Una **clave de API de Gemini** (gratuita): https://aistudio.google.com/apikey
  (solo requiere una cuenta de Google normal; no necesita Google Cloud ni tarjeta).
- **Git** (para colaborar).

---

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

# 2. Crear un entorno virtual e instalar dependencias
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> En Windows, el ejecutable está en `venv\Scripts\` en vez de `venv/bin/`.

---

## ⚙️ Configuración

Antes de arrancar, define **dos variables de entorno**:

| Variable         | Qué es                                              | Ejemplo                |
|------------------|-----------------------------------------------------|------------------------|
| `GEMINI_API_KEY` | Tu clave de Gemini (¡no la compartas ni la subas!)  | `AIza...`              |
| `COLABORADOR`    | Tu nombre/identificador (define tu archivo de datos)| `ricardo`              |

**macOS / Linux:**
```bash
export GEMINI_API_KEY="TU_CLAVE_AQUI"
export COLABORADOR="ricardo"
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="TU_CLAVE_AQUI"
$env:COLABORADOR="ricardo"
```

> ⚠️ Cada quien debe poner un `COLABORADOR` **distinto** (su nombre). Eso garantiza que
> cada uno escriba en su propio archivo `datos/heridos_<colaborador>.csv` y no haya choques.

---

## 🖥️ Uso diario

```bash
export GEMINI_API_KEY="TU_CLAVE_AQUI"
export COLABORADOR="ricardo"
./venv/bin/python app.py
```

Luego abre **http://localhost:5000** en el navegador y:

1. Toca la zona roja y **elige una captura/foto** de la lista (galería, archivos o cámara).
2. (Opcional) Escribe la **ubicación por defecto** (ej. *La Guaira*). Solo se aplica si la
   lista no indica una ubicación propia.
3. Pulsa **Procesar y Subir**. Verás los pacientes extraídos y se guardan en tu CSV.
4. Repite con todas tus fotos. Tu archivo `datos/heridos_<tunombre>.csv` se va llenando.

---

## 📱 Acceso desde el móvil

El móvil debe estar en la **misma red WiFi** que la computadora que corre la app.

1. Averigua la IP local de tu computadora:
   - macOS: `ipconfig getifaddr en0`
   - Windows: `ipconfig` (busca "Dirección IPv4")
2. En el móvil abre: `http://IP_DE_TU_PC:5000` (ej. `http://192.168.100.149:5000`).

> Si no carga, suele ser el **firewall** del sistema o que no están en la misma WiFi.

---

## 🤝 Reglas para colaborar en GitHub (IMPORTANTE)

El sistema está diseñado para que **nunca haya conflictos**, pero hay que respetar estas reglas:

### ✅ SÍ
1. **Cada colaborador usa un `COLABORADOR` único** (su nombre). Tu archivo es
   `datos/heridos_<tunombre>.csv` y **solo tú lo tocas**.
2. **Antes de empezar a trabajar**, actualiza el repo:
   ```bash
   git pull
   ```
3. **Al terminar tu tanda** (o cada cierto rato), sube SOLO tu archivo:
   ```bash
   git add datos/heridos_<tunombre>.csv
   git commit -m "datos: <tunombre> +N pacientes (zona X)"
   git push
   ```

### ❌ NO
- ❌ No edites el CSV de **otro** colaborador.
- ❌ No subas tu **API key** (`api,txt`, `.env`, etc.). Ya están en `.gitignore`.
- ❌ No subas la carpeta `venv/`.
- ❌ No commitees `heridos_consolidado.xlsx` salvo que seas el **coordinador** (ver abajo).

> **¿Por qué un archivo por persona?** Git no sabe fusionar dos cambios en el mismo
> archivo binario/Excel. Con un CSV por persona, dos colaboradores **nunca tocan el mismo
> archivo**, así que `git pull` y `git push` siempre funcionan sin conflictos.

---

## 📊 Consolidar el Excel final

> **¿Quién consolida?** Una sola persona designada como **coordinador**. Si varios
> generan y suben el consolidado a la vez, volverían los conflictos binarios. Por eso
> **solo el coordinador** ejecuta este paso y comparte el resultado.

El coordinador hace:

```bash
git pull                       # traer todos los CSV actualizados
./venv/bin/python consolidar.py
```

Esto lee **todos** los `datos/heridos_*.csv`, elimina duplicados globalmente
(conservando el registro más completo) y genera:

- `heridos_consolidado.xlsx` — el Excel final.
- `heridos_consolidado.csv` — versión en texto.

Por defecto estos dos archivos están en `.gitignore` (son artefactos generados). El
coordinador los comparte por el canal que prefiera (Drive, WhatsApp, etc.). Si prefieres
que el Excel **viva en el repo**, borra esas dos líneas del `.gitignore`; recuerda que
entonces **solo el coordinador** debe commitearlo para evitar conflictos.

---

## 📁 Estructura del proyecto

```
.
├── app.py                  # Servidor Flask + OCR con Gemini + guardado en CSV
├── consolidar.py           # Junta todos los CSV en el Excel final (lo corre el coordinador)
├── requirements.txt        # Dependencias de Python
├── templates/
│   └── index.html          # Interfaz web (móvil)
├── datos/                  # Un CSV por colaborador (esto es lo que se versiona)
│   ├── heridos_ricardo.csv
│   └── heridos_ana.csv
├── .gitignore
└── README.md
```

---

## 🛠️ Problemas comunes

| Síntoma | Causa / Solución |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | No instalaste las dependencias o no usas el venv. Usa `./venv/bin/python app.py`. |
| `404 ... gemini-X is not found` | El modelo fue retirado. Cambia `GEMINI_MODEL` en `app.py` por uno vigente (ej. `gemini-2.5-flash`). |
| En el móvil no deja elegir foto | Recarga la página; el selector abre galería/archivos/cámara. |
| La página no carga en el móvil | Firewall del PC o no están en la misma WiFi. |
| `Cliente Gemini no disponible` | Falta `export GEMINI_API_KEY=...` en esa terminal. |

---

## 🔐 Seguridad

- **Nunca** subas tu `GEMINI_API_KEY` al repositorio. El `.gitignore` ya bloquea
  `api,txt`, `.env` y similares, pero verifica antes de cada `git push`.
- Si tu clave se expuso alguna vez, **revócala y crea una nueva** en
  https://aistudio.google.com/apikey.
- Los datos de pacientes son **información sensible**. Mantén el repositorio **privado**
  y comparte el acceso solo con el equipo autorizado.
