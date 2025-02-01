import json
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from aimanager.agent.builder import LLMAgentBuilder
from apps.llmanager.repositories.conversation import ConversationRepository
from apps.llmanager.repositories.provider_config import ConfigRepository
from apps.llmanager.repositories.agent import AgentRepository
from apps.llmanager.serializers import AgentSerializer, ConversationSerializer

logger = logging.getLogger("django")


class ChatbotPromptView(APIView):
    def post(self, request, conversation_id=None):
        try:
            data = request.data
            prompt = data.get("prompt")

            if not prompt:
                return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)

            agent_id = data.get("agent_id")
            user_id = request.user.id

            agent = ConfigRepository.get_agent()
            model = ConfigRepository.get_model()
            provider = ConfigRepository.get_provider()

            system_prompt = None
            if agent_id:
                system_prompt = AgentRepository.get_system_prompt_for_agent(agent_id)
            agent = LLMAgentBuilder.build(agent_name=agent, provider=provider, model=model, system_prompt=system_prompt)
            conversation = ConversationRepository.get(conversation_id)
            if not conversation.title:
                ConversationRepository.update_title(conversation_id, prompt[:20])
            response_generator = agent.generate_response_stream(prompt, user_id, conversation_id)
            response = StreamingHttpResponse(response_generator, content_type="text/event-stream; charset=utf-8")
            response["Cache-Control"] = "no-cache"
            return response
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("error", exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, conversation_id=None):
        try:
            user_id = request.user.id
            agent = ConfigRepository.get_agent()
            model = ConfigRepository.get_model()
            provider = ConfigRepository.get_provider()
            agent = LLMAgentBuilder.build(agent_name=agent, provider=provider, model=model)
            conversation = agent.get_conversation(user_id, conversation_id)

            return Response(conversation, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("error", exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, conversation_id=None):
        try:
            user_id = request.user.id

            agent = ConfigRepository.get_agent()
            model = ConfigRepository.get_model()
            provider = ConfigRepository.get_provider()
            agent = LLMAgentBuilder.build(agent_name=agent, provider=provider, model=model)
            agent.clear_conversation(user_id, conversation_id)
            ConversationRepository.delete(conversation_id)
            return Response({"message": "Conversation cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("error", exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationView(APIView):
    def post(self, request):
        try:
            user_id = request.user.id
            conversation = ConversationRepository.create(user_id)
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("error", exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user_id = request.user.id
            conversations = ConversationRepository.get_user_conversations(user_id)
            return Response(ConversationSerializer(conversations, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("error", exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentRepository.get_active_agents()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]
