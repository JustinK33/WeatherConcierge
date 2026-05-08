# Weather Concierge

A compact, AI-powered weather assistant API that combines LangChain tools with Google’s generative models and OpenWeather for accurate current conditions and short forecasts.

## Highlights
- Conversational weather assistant powered by a LangChain agent and Google Generative AI.
- Tooling integration with OpenWeather (current + 5-day forecast summary).
- FastAPI backend with typed Pydantic schemas and session-based chat.
- Docker-ready: single-step build and run.

## Tech Stack
- Python 3.11
- FastAPI
- LangChain + langchain-google-genai
- Google Generative AI (configurable model)
- OpenWeather API for weather data

## Features
- POST `/weather/current` — Get current weather summary for a city.
- POST `/weather/forecast` — Get a simplified multi-day forecast (1-5 days).
- POST `/chat` — Conversational interface powered by a LangChain agent that uses the weather tools when relevant.
- `/health` — Simple health check endpoint.

## Quickstart (local)
1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (you can copy from `.env.example`) and set your keys:

```bash
cp .env.example .env
# then edit .env and add your WEATHER_API_KEY and GOOGLE_API_KEY
```

4. Run the app:

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

5. Open docs at `http://localhost:8000/docs` to explore the API interactively.

## Docker
Build and run the container:

```bash
docker build -t weather-concierge:latest .
docker run -e WEATHER_API_KEY=your_openweather_key -e GOOGLE_API_KEY=your_google_key -p 8000:8000 weather-concierge:latest
```

## Environment Variables
Use `.env` or environment variables to configure the app. See `.env.example`.
- `WEATHER_API_KEY` — OpenWeather API key (required for weather tools).
- `GOOGLE_API_KEY` — Google Generative AI key (optional for local testing if you use a different model or mock).
- `AI_MODEL` — Optional model name (default configured in `app/config.py`).

## API Examples

Current weather

```bash
curl -X POST "http://localhost:8000/weather/current" -H "Content-Type: application/json" -d '{"location": {"city": "New York", "country_code": "US"}}'
```

Chat (conversational)

```bash
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"message": "What's the weather like in Boston today?"}'
```

## Project layout
- `app/` — FastAPI app, agent, tools and schemas.
- `Dockerfile` — Container image for running the service.
- `requirements.txt` — Python dependencies.

## Architecture (Overview)
The service follows a modular, production-friendly architecture designed for horizontal scaling and observability:

- **API Layer (FastAPI):** lightweight HTTP + WebSocket endpoints for programmatic and real-time access.
- **Agent Layer (LangChain + Google Gen-AI):** a specialized weather agent that composes tool calls and LLM responses.
- **Tooling Layer:** deterministic tools that call external systems (OpenWeather). Tools are pure functions that return structured text and are safe to test.
- **Session Store:** in-memory session store for demo; replaceable with Redis for persistence and multi-instance support.
- **Telemetry & Observability:** Prometheus metrics endpoint and request counters for monitoring.
- **Background Jobs:** scheduled alerts and async tasks for periodic checks (pluggable via Celery / RQ / APScheduler).

Design goals: minimal latency for simple queries, graceful degradation when external APIs fail, and clear separation between LLM logic and deterministic tools so the system is auditable.

## Impressive Features Added
- Real-time conversational WebSocket chat (`/ws/chat`) enabling interactive sessions and push-style updates.
- Prometheus metrics (`/metrics`) for request counts and latency, ready for Grafana dashboards.
- Clear upgrade path to production: Redis-backed sessions, Kubernetes-ready Docker image, horizontal autoscaling, and CI/CD.

## What's included in this update
- `app/api.py`: WebSocket chat endpoint and metrics mounting.
- `app/telemetry.py`: Prometheus metrics utilities and middleware.
- `requirements.txt`: added `prometheus-client`.


## Next steps / Ideas to make it more impressive
- Add an OpenAPI client example and a small demo web UI.
- Add CI (GitHub Actions) with linting and automated builds.
- Add unit tests for `app/tools/weather.py` using VCR or HTTP mocking.
- Add a small demo script that queries the API and prints a nice formatted report.

## Contributing
PRs welcome. For major changes, open an issue first to discuss the design.

## License
MIT# Weather Chat Service API

A FastAPI backend that exposes a weather-focused chat service.  
It uses a LangChain agent with weather tools to answer questions like  
“what’s the weather in New Brunswick today?” or “what’s the forecast for the next 3 days?”

If the user asks about something that isn’t weather, the agent politely says it only handles weather questions.

---

## Tech Stack

- Python
- FastAPI
- LangChain
- Pydantic
- OpenAI API
- Docker
- Uvicorn

---

## Features

- Built with `create_agent` from LangChain:
  - Uses `settings.OPENAI_MODEL` as the LLM.
  - Has access to `get_current_weather` and `get_forecast` tools.
- **System prompt behavior:**
  - If the question is about weather or forecast, it calls the tools.
  - If the question is not about weather, it briefly says it only handles weather questions.
  - 
 ---
 
## What I Learned From This Project

Using LangChain agents with tools
I learned how to use create_agent with custom tools (get_current_weather, get_forecast) and a system prompt so the agent automatically decides when to call them.

Building a FastAPI service around an LLM
I saw how to wrap an LLM agent into clean HTTP endpoints (/weather/current, /weather/forecast, /chat) using FastAPI and Pydantic models.

Managing chat sessions and message history
By using ChatSession, ChatMessage, and an in-memory SESSION_STORE, I learned how to keep per-session message history and convert it to LangChain HumanMessage / AIMessage / SystemMessage.

---

## Running the Project

### To run the project locally, follow these steps:

  1. Clone the repo (git clone <url>)
  2. Create a virtual environment (python3 -m venv venv)
  3. Activate the environment (source venv/bin/activate)
  4. Install requirements (pip install -r requirements.txt)
  5. Set or export your OpenAI API key (in .env or export ...)
  6. Run locally (uvicorn app.main:app --reload)
     
### Run with Docker

  2. Build image (docker build -t weather-chat-service -f dockerfile .)
  3. Run image (docker run --rm -p 8000:8000 --env-file .env weather-chat-service) # make sure API key is in .env
