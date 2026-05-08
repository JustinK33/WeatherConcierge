from uuid import uuid4
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from app import schemas
from app.agent import agent
from app.services import weather_service
from app.services.session_store import SessionStore
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from app.telemetry import mount_metrics, RequestMetricsMiddleware
import asyncio

app = FastAPI(title="Weather Chat Service", version="0.2.0")
app.add_middleware(RequestMetricsMiddleware)
mount_metrics(app)

# pluggable session store
session_store = SessionStore()

@app.get("/health")
def health_check():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/weather/current", response_model=schemas.CurrentWeatherResponse)
def current_weather(req: schemas.CurrentWeatherRequest):
    text = weather_service.get_current(req.location.city)
    summary = schemas.WeatherSummary(
        description=text,
        temperature=0.0,
        feels_like=0.0,
        humidity=None,
        wind_speed=None,
        temperature_unit=req.temperature_unit,
        speed_unit=schemas.SpeedUnit.mph,
    )

    return schemas.CurrentWeatherResponse(
        location=req.location,
        summary=summary,
        raw_source=None,
    )

@app.post("/weather/forecast", response_model=schemas.ForecastResponse)
def forecast(req: schemas.ForecastRequest):
    text = weather_service.get_multi_day_forecast(req.location.city, req.days)
    day = schemas.ForecastDay(
        date=datetime.utcnow(),
        summary=schemas.WeatherSummary(
            description=text,
            temperature=0.0,
            feels_like=0.0,
            humidity=None,
            wind_speed=None,
            temperature_unit=req.temperature_unit,
            speed_unit=schemas.SpeedUnit.mph,
        ),
    )

    return schemas.ForecastResponse(
        location=req.location,
        days=[day],
        raw_source=None,
    )

def _get_or_create_session(session_id: str | None) -> schemas.ChatSession:
    session = session_store.get(session_id) if session_id else None
    if session is None:
        new_id = str(uuid4())
        session = schemas.ChatSession(session_id=new_id, messages=[])
        session_store.create(session)
        return session
    return session



@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            session_id = data.get("session_id")

            session = _get_or_create_session(session_id)

            user_msg = schemas.ChatMessage(
                role=schemas.ChatMessageRole.user,
                content=message,
            )
            session.messages.append(user_msg)

            # Build LangChain message list
            lc_messages: list[BaseMessage] = []
            for m in session.messages:
                if m.role == schemas.ChatMessageRole.user:
                    lc_messages.append(HumanMessage(content=m.content))
                elif m.role == schemas.ChatMessageRole.assistant:
                    lc_messages.append(AIMessage(content=m.content))
                else:
                    lc_messages.append(SystemMessage(content=m.content))

            state = {"messages": lc_messages}

            # agent.invoke may be blocking; run in thread
            try:
                result = await asyncio.get_event_loop().run_in_executor(None, lambda: agent.invoke(state))
            except Exception as e:
                await websocket.send_json({"error": str(e)})
                continue

            reply_content = (
                result["messages"][-1].content
                if isinstance(result, dict) and "messages" in result
                else str(result)
            )

            assistant_msg = schemas.ChatMessage(
                role=schemas.ChatMessageRole.assistant,
                content=reply_content,
            )
            session.messages.append(assistant_msg)

            SESSION_STORE[session.session_id] = session

            await websocket.send_json({"reply": reply_content, "session_id": session.session_id})

    except WebSocketDisconnect:
        return



@app.post("/chat", response_model=schemas.ChatResponse)
def chat(req: schemas.ChatRequest):
    session = _get_or_create_session(req.session_id)

    if req.preferences_override is not None:
        session.preferences = req.preferences_override

    user_msg = schemas.ChatMessage(
        role=schemas.ChatMessageRole.user,
        content=req.message,
    )
    session.messages.append(user_msg)
    
    lc_messages: list[BaseMessage] = []
    for m in session.messages:
        if m.role == schemas.ChatMessageRole.user:
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == schemas.ChatMessageRole.assistant:
            lc_messages.append(AIMessage(content=m.content))
        else:
            lc_messages.append(SystemMessage(content=m.content))

    state: Dict[str, Any] = {"messages": lc_messages}

    try:
        result = agent.invoke(state)  # type: ignore[arg-type]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    reply_content = (
        result["messages"][-1].content
        if isinstance(result, dict) and "messages" in result
        else str(result)
    )

    assistant_msg = schemas.ChatMessage(
        role=schemas.ChatMessageRole.assistant,
        content=reply_content,
    )
    session.messages.append(assistant_msg)

    SESSION_STORE[session.session_id] = session

    return schemas.ChatResponse(
        session_id=session.session_id,
        reply=reply_content,
        session=session,
        detected_location=None,
    )