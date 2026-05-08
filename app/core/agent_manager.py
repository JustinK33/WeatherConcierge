from typing import Any, Dict
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about the weather. "
    "Use the tools get_current_weather and get_forecast whenever the user "
    "asks about weather or forecast. "
    "If the question is not about weather, briefly say you only handle weather questions."
)


class AgentManager:
    _agent = None

    @classmethod
    def build_agent(cls):
        llm = ChatGoogleGenerativeAI(
            model=settings.AI_MODEL,
            api_key=settings.GOOGLE_API_KEY,
        )

        agent = create_agent(
            model=llm,
            tools=[],  # tools will be provided at invoke time if needed
            system_prompt=SYSTEM_PROMPT,
        )
        return agent

    @classmethod
    def get_agent(cls):
        if cls._agent is None:
            cls._agent = cls.build_agent()
        return cls._agent

    @classmethod
    def invoke(cls, state: Dict[str, Any]):
        agent = cls.get_agent()
        return agent.invoke(state)
