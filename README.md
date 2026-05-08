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
## Contributing
PRs welcome. For major changes, open an issue first to discuss the design.

## License
MIT

## Continuous Integration
This repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

- Installs dependencies from `requirements.txt`.
- Byte-compiles the codebase to detect syntax errors.
- Runs a lightweight FastAPI `TestClient` health check against the `app`.
- Runs `pytest` if tests are present (non-fatal if none exist).

The CI badge at the top of this README links to the workflow run history.
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
