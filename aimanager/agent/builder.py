from ._interface import AIAgentInterface, AsyncAIAgentInterface
from ._base import BaseAgent, BaseAsyncAgent


class LLMAgentBuilder:
    @staticmethod
    def build(agent_name: str, *args, **kwargs) -> AIAgentInterface:
        if agent_name:
            for agent in [BaseAgent]:
                if agent.name == agent_name:
                    return agent(*args, **kwargs)
        else:
            return BaseAgent(*args, **kwargs)


class AsyncLLMAgentBuilder:
    @staticmethod
    def build(agent_name: str, *args, **kwargs) -> AsyncAIAgentInterface:
        if agent_name:
            for agent in [BaseAsyncAgent]:
                if agent.name == agent_name:
                    return agent(*args, **kwargs)
        else:
            return BaseAsyncAgent(*args, **kwargs)
