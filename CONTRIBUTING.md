# 🤝 Guía rápida para colaboradores

Gracias por ayudar a digitalizar las listas de heridos. Procesarás capturas con la app y
le enviarás tu archivo de datos al **coordinador** por el canal privado del equipo.

> 🔒 **MUY IMPORTANTE — privacidad:** Los datos de los pacientes (nombres, cédulas,
> ubicaciones, y datos de **menores**) son **información sensible**. **NUNCA** los subas a
> GitHub ni a ningún sitio público. Solo se comparten por el **canal privado** que indique
> el coordinador (ej. grupo cerrado / Drive con permisos).

> ⚠️ Los datos provienen de capturas de redes sociales y los lee una IA: pueden tener
> errores y **no son una fuente oficial**. (Disclaimer completo en el [README](README.md).)

---

## ✅ Lo que necesitas

- **Python 3.10+** instalado.
- **Git** instalado (solo para descargar el código).
- Una **clave gratuita de Gemini**: https://aistudio.google.com/apikey → "Crear clave de
  API" → cópiala. (No necesita tarjeta ni Google Cloud.)
- El **link del canal privado** del equipo para enviar tu CSV (pídeselo al coordinador).

---

## 🛠️ Instalación (solo la primera vez)

```bash
# 1. Descarga el código
git clone https://github.com/ricdjulio/ConsolidadoHeridosVZLA2026.git
cd ConsolidadoHeridosVZLA2026

# 2. Crea el entorno e instala dependencias
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> En **Windows** usa `venv\Scripts\python` en lugar de `./venv/bin/python`.

---

## ▶️ Cada vez que vayas a cargar datos

### 1. Actualiza el código (por si hubo mejoras)
```bash
git pull
```

### 2. Arranca la app (pon TU nombre en COLABORADOR)
```bash
export GEMINI_API_KEY="TU_CLAVE_DE_GEMINI"
export COLABORADOR="tunombre"          # ej: maria  (¡usa siempre el mismo!)
./venv/bin/python app.py
```

### 3. Procesa las capturas
- En la computadora: http://localhost:5000
- Desde el **móvil** (misma WiFi que la PC): `http://IP_DE_LA_PC:5000`
- Toca la zona roja → elige la captura → (opcional) escribe la ubicación por defecto →
  **Procesar y Subir**. Repite con todas tus capturas.

### 4. Descarga tu CSV y envíalo al coordinador
- Pulsa el botón verde **⬇️ Descargar mi CSV**.
- Envía ese archivo (`heridos_tunombre.csv`) al **coordinador** por el **canal privado**.
- El coordinador lo junta con los demás y genera el consolidado.

¡Y listo! 🎉

---

## 📏 Reglas de oro

| ✅ Haz esto | ❌ No hagas esto |
|---|---|
| Usa **siempre el mismo** `COLABORADOR` (tu nombre) | Cambiar tu nombre cada vez |
| Enviar tu CSV por el **canal privado** | **Subir datos de pacientes a GitHub** o redes |
| Guardar tu API key solo en tu PC | Subir tu API key (`.env`, `api,txt`) a ningún lado |
| Borrar las capturas cuando ya no las necesites | Difundir las capturas o los datos públicamente |

> El repositorio es **solo el código**. Los **datos nunca** van al repo: el `.gitignore` ya
> los bloquea, pero por seguridad nunca fuerces su subida.

---

## 🆘 Si algo falla

| Problema | Solución |
|---|---|
| `No module named 'flask'` | Usa `./venv/bin/python app.py`, no `python app.py`. |
| `Cliente Gemini no disponible` | Te faltó `export GEMINI_API_KEY=...` en esa terminal. |
| `error 404 ... gemini ...` | Avisa al coordinador (hay que actualizar el modelo). |
| El móvil no abre la página | Deben estar en la **misma WiFi**; revisa el firewall de la PC. |

Ante cualquier duda, escribe al coordinador. ¡Gracias por colaborar! 🙏
