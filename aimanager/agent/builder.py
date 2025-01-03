from ._interface import AIAgentInterface
from ._base import BaseAgent


class LLMAgentBuilder:
    @staticmethod
    def build(agent_name: str, agent_instruction: str = None, *args, **kwargs) -> AIAgentInterface:
        if agent_name:
            for agent in [BaseAgent]:
                if agent.name == agent_name:
                    return agent(*args, **kwargs)
        else:
            if agent_instruction is None:
                raise ValueError("Agent name or instruction is required.")
