from typing import Any, Dict
from types import SimpleNamespace
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
        # If no API key is configured (e.g., in CI or local tests), return
        # a lightweight mock agent that implements `invoke(state)` so
        # imports and tests don't require external API credentials.
        if not settings.GOOGLE_API_KEY:
            class MockAgent:
                def invoke(self, state: Dict[str, Any]):
                    # Return a structure compatible with the code that expects
                    # {'messages': [<obj with .content>]}
                    reply = SimpleNamespace(content="(mock) no API key configured; agent disabled")
                    return {"messages": [reply]}

            return MockAgent()

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
