# Curso Agentes LangGraph

Guía práctica para clonar este repositorio, instalar las dependencias y ejecutar los agentes usando Windows. Incluye un recorrido de la estructura del código y enlaces a documentación adicional.

> 📘 ¿Buscas una descripción detallada de cada agente y servicio? Revisa [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requisitos previos

Asegúrate de contar con las siguientes herramientas en tu equipo Windows (puedes instalarlas desde PowerShell):

```powershell
# Python 3.12 y Git
winget install Python.Python.3.12 -s winget
winget install Git.Git -s winget

# (Opcional) Docker Desktop para levantar Postgres en contenedor
winget install Docker.DockerDesktop -s winget
```

Verifica las instalaciones:

```powershell
python --version
pip --version
git --version
# opcional
docker --version
```

## Paso a paso: ejecutar el proyecto

### 1. Clonar el repositorio

```powershell
git clone https://github.com/<tu-usuario>/curso-agentes-langgraph.git
cd curso-agentes-langgraph
```

### 2. Crear y activar el entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

> 💡 Si PowerShell bloquea la activación del entorno, ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` una sola vez.

### 3. Instalar dependencias

```powershell
pip install -e .
pip install "langgraph-cli[inmem]"
```

Esto instalará FastAPI, LangGraph, los conectores de modelos (OpenAI y Anthropic) y la CLI de LangGraph definida en `pyproject.toml`。【F:pyproject.toml†L1-L24】

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con tus claves de proveedor. Usa PowerShell para generarlo rápidamente:

```powershell
@"
OPENAI_API_KEY=tu_clave_de_openai
ANTHROPIC_API_KEY=tu_clave_de_anthropic
LANGCHAIN_API_KEY=opcional_si_usas_langsmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=curso-agentes-langgraph
"@ | Out-File -FilePath .env -Encoding utf8
```

El archivo será leído automáticamente por la API y por la CLI de LangGraph.【F:src/api/main.py†L1-L16】【F:langgraph.json†L1-L13】

### 5. (Opcional) Levantar Postgres con Docker

El proyecto usa Postgres como almacén de checkpoints. Si tienes Docker Desktop puedes iniciarlo con:

```powershell
docker compose up -d postgres
```

Esto creará una base llamada `my_course_agent` accesible en `postgresql://postgres:postgres@localhost:5432/my_course_agent`, la misma URL configurada en `src/api/db.py`.【F:src/api/db.py†L1-L24】【F:docker-compose.yml†L1-L23】

### 6. Ejecutar la API de soporte

Con el entorno virtual activo y `.env` configurado, lanza el servidor FastAPI:

```powershell
uvicorn src.api.main:app --reload
```

- La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.
- El endpoint `POST /chat/{chat_id}` crea una conversación o la retoma usando el checkpointer de Postgres.【F:src/api/main.py†L18-L36】
- El endpoint `POST /chat/{chat_id}/stream` entrega respuestas en streaming.【F:src/api/main.py†L38-L44】

### 7. Probar agentes con LangGraph CLI

Los agentes definidos en `langgraph.json` pueden ejecutarse con el modo interactivo de la CLI:

```powershell
langgraph dev --graph support
```

Reemplaza `support` por cualquiera de los agentes registrados (`agent`, `simple`, `rag`, `react`, `code_review`, `orchestrator`, `evaluator`, etc.).【F:langgraph.json†L3-L12】

## Configuración alternativa con `uv` (opcional)

Si prefieres gestionar dependencias con [uv](https://github.com/astral-sh/uv):

```powershell
# Instalar uv
irm https://astral.sh/uv/install.ps1 | iex

# Crear el proyecto
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -e .
uv pip install "langgraph-cli[inmem]" --dev
```

Puedes ejecutar cualquier comando con `uv run`, por ejemplo:

```powershell
uv run langgraph dev --graph support
uv run uvicorn src.api.main:app --reload
```

## Estructura del proyecto

Consulta [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para un resumen completo de cada agente, nodo y servicio.

## Recursos útiles

- [Documentación de LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangSmith](https://docs.smith.langchain.com/) (para trazas si habilitas `LANGCHAIN_TRACING_V2`)

