from apps.llmanager.models import Agent


class AgentRepository:
    """Repository wrapper over django models for Agent model"""

    @staticmethod
    def get(agent_id: int):
        return Agent.objects.get(id=agent_id)

    @staticmethod
    def get_system_prompt_for_agent(agent_id: int):
        agent = AgentRepository.get(agent_id=agent_id)
        return agent.instructions

    @staticmethod
    def get_active_agents():
        return Agent.objects.filter(is_active=True)

    @staticmethod
    def get_agent_by_name(agent_name: str):
        return Agent.objects.get(name=agent_name)

    @staticmethod
    def create_agent(
        name: str, description: str, instructions: str, model: str, provider: str, metadata: dict, is_active: bool
    ):
        return Agent.objects.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model,
            provider=provider,
            metadata=metadata,
            is_active=is_active,
        )

    @staticmethod
    def update_agent(
        agent_id: int,
        name: str,
        description: str,
        instructions: str,
        model: str,
        provider: str,
        metadata: dict,
        is_active: bool,
    ):
        agent = Agent.objects.get(id=agent_id)
        agent.name = name
        agent.description = description
        agent.instructions = instructions
        agent.model = model
        agent.provider = provider
        agent.metadata = metadata
        agent.is_active = is_active
        agent.save()
        return agent

    @staticmethod
    def delete_agent(agent_id: int):
        agent = Agent.objects.get(id=agent_id)
        agent.delete()
        return agent
