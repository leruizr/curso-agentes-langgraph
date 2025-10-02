# Arquitectura y componentes

Este documento describe la estructura del proyecto y el propósito de cada agente, nodo y servicio disponible en el repositorio.

## Visión general del proyecto

El repositorio contiene una colección de agentes construidos con [LangGraph](https://langchain-ai.github.io/langgraph/) y utilidades asociadas para orquestar conversaciones, realizar consultas RAG, ejecutar revisiones de código y exponer un servicio web basado en FastAPI. Cada agente se registra en `langgraph.json` para que pueda ejecutarse con la CLI de LangGraph o integrarse dentro de la API.【F:langgraph.json†L1-L13】

## Resumen de carpetas

| Ruta | Descripción |
| --- | --- |
| `src/agents` | Colección de agentes de ejemplo y productivos que cubren distintos patrones de LangGraph. |
| `src/agents/support` | Agente de soporte con múltiples nodos, herramientas y ruteo condicional. |
| `src/api` | API de FastAPI que expone el agente de soporte y configura la persistencia de checkpoints en Postgres. |
| `docker-compose.yml` | Contenedor de Postgres listo para usarse como almacén de checkpoints. |
| `notebooks/` | Cuadernos de soporte para experimentar con los agentes. |

## Agentes individuales (`src/agents`)

### `main.py`
Agente mínimo que delega en `create_agent` de LangChain. Implementa una única herramienta (`get_weather`) y configura un modelo GPT-4o mini con un prompt de asistente genérico.【F:src/agents/main.py†L1-L14】

### `simple.py`
Demuestra cómo construir un grafo con un único nodo (`node_1`). El estado hereda de `MessagesState` para conservar el historial de conversación y campos adicionales como `customer_name` y `my_age`. El nodo genera respuestas con `init_chat_model`, actualiza el estado y concluye el flujo con un grafo `START -> node_1 -> END`.【F:src/agents/simple.py†L1-L29】

### `react.py`
Ejemplo de agente estilo ReAct que expone dos herramientas (`get_products` y `get_weather`) respaldadas por llamadas HTTP. El agente usa un modelo Claude Opus y un prompt en español orientado a ventas.【F:src/agents/react.py†L1-L35】

### `code_review.py`
Grafo que coordina tres nodos: `security_review`, `maintainability_review` y `aggregator`. Cada revisión devuelve un esquema Pydantic (`SecurityReview`, `MaintainabilityReview`) generado por el modelo y el agregador sintetiza un resumen final. Los nodos se ejecutan en paralelo desde `START` y convergen en `aggregator`.【F:src/agents/code_review.py†L1-L62】【F:src/agents/code_review.py†L66-L76】

### `rag.py`
Implementa un flujo RAG con extracción de datos del usuario y respuesta asistida por herramientas. El estado guarda nombre, teléfono y edad; el nodo `extractor` usa un modelo estructurado (`ContactInfo`) para poblar el estado, mientras que `conversation` responde apoyándose en la herramienta `file_search`.【F:src/agents/rag.py†L1-L48】【F:src/agents/rag.py†L52-L73】

### `evaluator.py`
Patrón generador-evaluador: `generator_node` crea chistes basados en el tópico y feedback previo, y `evaluator_node` califica con un modelo estructurado (`Feedback`). Si el chiste no es gracioso, el grafo regresa a `generator_node`; en caso contrario termina en `END`.【F:src/agents/evaluator.py†L1-L50】【F:src/agents/evaluator.py†L54-L69】

### `orchestrator.py`
Ejemplo de orquestador que selecciona dinámicamente nodos de trabajo. El nodo `orchestrator` devuelve una lista aleatoria de nodos y `assign_nodes` envía mensajes a cada uno usando `Send`. Todos los nodos convergen en `aggregator` antes de finalizar.【F:src/agents/orchestrator.py†L1-L43】

## Agente de soporte (`src/agents/support`)

El agente de soporte es un grafo multi-nodo pensado para manejar conversaciones con clientes y flujo de reservas médicas.【F:src/agents/support/agent.py†L1-L21】 Sus elementos principales son:

- **Estado compartido** (`state.py`): extiende `MessagesState` con campos para nombre del cliente, teléfono y edad.【F:src/agents/support/state.py†L1-L6】
- **Extractor** (`nodes/extractor/node.py`): obtiene datos de contacto mediante salida estructurada y solo actúa cuando faltan datos en el estado.【F:src/agents/support/nodes/extractor/node.py†L1-L26】
- **Conversación** (`nodes/conversation/node.py`): genera respuestas contextualizadas con el nombre del usuario y puede usar la herramienta de búsqueda de archivos para responder preguntas.【F:src/agents/support/nodes/conversation/node.py†L1-L21】【F:src/agents/support/nodes/conversation/tools.py†L1-L6】
- **Reserva médica** (`nodes/booking/node.py`): agente ReAct especializado en reservas que combina herramientas de disponibilidad y confirmación con un prompt detallado.【F:src/agents/support/nodes/booking/node.py†L1-L10】【F:src/agents/support/nodes/booking/tools.py†L1-L16】【F:src/agents/support/nodes/booking/prompt.py†L1-L23】
- **Ruteo de intención** (`routes/intent/route.py`): decide si continuar la conversación general o activar el nodo de reservas según el historial de mensajes.【F:src/agents/support/routes/intent/route.py†L1-L22】【F:src/agents/support/routes/intent/prompt.py†L1-L6】

El grafo une estos componentes con una ruta inicial hacia `extractor`, luego deriva condicionalmente a `conversation` o `booking`, y finaliza cuando cualquiera de los nodos retorna un resultado.【F:src/agents/support/agent.py†L8-L21】

## API (`src/api`)

La API utiliza FastAPI para exponer el agente de soporte vía HTTP.【F:src/api/main.py†L1-L44】 La aplicación:

1. Carga variables desde `.env` y crea la app con un `lifespan` que inyecta un `PostgresSaver` compartido.【F:src/api/main.py†L1-L16】【F:src/api/db.py†L1-L24】
2. Define un endpoint `POST /chat/{chat_id}` que reconstruye el grafo con el checkpointer, agrega el mensaje del usuario y devuelve el historial completo.【F:src/api/main.py†L18-L36】
3. Ofrece un endpoint `POST /chat/{chat_id}/stream` que entrega respuestas en streaming usando `StreamingResponse`.【F:src/api/main.py†L38-L44】

## Persistencia de checkpoints

`src/api/db.py` configura un `PostgresSaver` apuntando a una instancia local de Postgres (puede levantarse con `docker-compose.yml`). Esta configuración inicializa el esquema al arrancar la aplicación y expone una dependencia `CheckpointerDep` para inyectar el saver en los endpoints.【F:src/api/db.py†L1-L24】

## Cómo ejecutar un agente

Todos los agentes están registrados en `langgraph.json`, por lo que es posible iniciar el entorno interactivo de LangGraph ejecutando:

```powershell
langgraph dev --graph <nombre_del_agente>
```

Sustituye `<nombre_del_agente>` por cualquiera de las claves definidas (`agent`, `simple`, `rag`, `support`, etc.).【F:langgraph.json†L3-L12】

