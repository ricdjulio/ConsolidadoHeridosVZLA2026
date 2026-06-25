# 🤝 Guía rápida para colaboradores

Gracias por ayudar a digitalizar las listas de heridos. Sigue estos pasos **una sola vez**
para instalar, y luego el flujo diario es muy corto.

> ⚠️ **Recuerda:** los datos provienen de capturas de redes sociales y los lee una IA, así
> que pueden tener errores. No es una fuente oficial. Trata la información de las personas
> con cuidado y confidencialidad. (Ver disclaimer completo en el [README](README.md).)

---

## ✅ Lo que necesitas

- **Python 3.10+** instalado.
- **Git** instalado.
- Una **clave gratuita de Gemini**: entra a https://aistudio.google.com/apikey con tu
  cuenta de Google → "Crear clave de API" → cópiala. (No necesita tarjeta ni Google Cloud.)
- Que el coordinador te haya dado **acceso al repositorio**.

---

## 🛠️ Instalación (solo la primera vez)

Como este es un repositorio **público**, contribuyes con el modelo **Fork + Pull Request**.
No necesitas invitación: cualquiera puede unirse.

```bash
# 1. Haz FORK del repo desde la web de GitHub (botón "Fork" arriba a la derecha).
#    Eso crea una copia tuya en https://github.com/TU_USUARIO/REPO

# 2. Clona TU fork (ojo: tu usuario, no el original)
git clone https://github.com/TU_USUARIO/REPO.git
cd REPO

# 3. Conecta el repo original como "upstream" para poder actualizar después
git remote add upstream https://github.com/USUARIO_ORIGINAL/REPO.git

# 4. Crea el entorno e instala dependencias
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

> En **Windows** usa `venv\Scripts\python` en lugar de `./venv/bin/python`.

---

## ▶️ Cada vez que vayas a cargar datos

### 1. Actualiza tu fork con los últimos datos
```bash
git pull upstream main
```

### 2. Arranca la app (pon TU nombre en COLABORADOR)
```bash
export GEMINI_API_KEY="TU_CLAVE_DE_GEMINI"
export COLABORADOR="tunombre"          # ej: maria  (¡usa siempre el mismo!)
./venv/bin/python app.py
```

### 3. Abre la app y procesa fotos
- En la computadora: http://localhost:5000
- Desde el **móvil** (misma WiFi que la PC): `http://IP_DE_LA_PC:5000`
- Toca la zona roja → elige la captura → (opcional) escribe la ubicación por defecto →
  **Procesar y Subir**. Repite con todas tus capturas.

### 4. Sube SOLO tu archivo a tu fork
```bash
git add datos/heridos_tunombre.csv
git commit -m "datos: tunombre +N pacientes"
git push origin main
```

### 5. Abre un Pull Request
- Ve a tu fork en GitHub: te saldrá un botón **"Compare & pull request"** → púlsalo →
  **"Create pull request"**.
- O por terminal, si tienes GitHub CLI: `gh pr create --fill`
- El coordinador lo revisará y lo aprobará. Como solo tocaste **tu** archivo, se aprueba
  sin conflictos. 🎉

> La próxima vez solo repites los pasos 1→5. ¡Gracias!

---

## 📏 Reglas de oro

| ✅ Haz esto | ❌ No hagas esto |
|---|---|
| Usa **siempre el mismo** `COLABORADOR` (tu nombre) | Cambiar tu nombre cada vez (creas archivos sueltos) |
| `git pull` **antes** de empezar | Trabajar sin actualizar primero |
| Sube **solo tu** `datos/heridos_tunombre.csv` | Editar el CSV de otra persona |
| Guardar tu API key solo en tu PC | Subir tu API key al repo (`.env`, `api,txt`, etc.) |
| Dejar que el **coordinador** consolide el Excel | Generar/subir `heridos_consolidado.xlsx` tú mismo |

> **¿Por qué cada quien su archivo?** Así nunca chocan dos personas en Git y `git push`
> siempre funciona sin conflictos.

---

## 🆘 Si algo falla

| Problema | Solución |
|---|---|
| `No module named 'flask'` | Usa `./venv/bin/python app.py`, no `python app.py`. |
| `Cliente Gemini no disponible` | Te faltó `export GEMINI_API_KEY=...` en esa terminal. |
| `error 404 ... gemini ...` | Avisa al coordinador (hay que actualizar el modelo). |
| El móvil no abre la página | Deben estar en la **misma WiFi**; revisa el firewall de la PC. |
| `git push` da error de conflicto | Casi seguro tocaste otro archivo. Avisa al coordinador. |

Ante cualquier duda, escribe al coordinador del proyecto. ¡Gracias por colaborar! 🙏
