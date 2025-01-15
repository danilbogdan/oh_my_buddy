import json
import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from aimanager.agent.builder import LLMAgentBuilder
from apps.llmanager.repositories.conversation import ConversationRepository
from apps.llmanager.repositories.provider_config import ConfigRepository

logger = logging.getLogger('django')


class ChatbotPromptView(APIView):

    def post(self, request):
        try:
            data = request.data
            prompt = data.get("prompt")

            if not prompt:
                return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)

            user_id = request.user.id
            agent = ConfigRepository.get_agent()
            model = ConfigRepository.get_model()
            provider = ConfigRepository.get_provider()
            agent = LLMAgentBuilder.build(agent_name=agent, provider=provider, model=model)
            response_generator = agent.generate_response_stream(prompt, user_id)
            response = StreamingHttpResponse(response_generator, content_type="text/event-stream")
            response["Cache-Control"] = "no-cache"
            return response
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error('error', exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user_id = request.user.id
            agent = ConfigRepository.get_agent()
            model = ConfigRepository.get_model()
            provider = ConfigRepository.get_provider()
            agent = LLMAgentBuilder.build(agent_name=agent, provider=provider, model=model)
            conversation = agent.get_conversation(user_id)

            return Response(conversation, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error('error', exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            user_id = request.user.id

            agent = LLMAgentBuilder.build(agent_name="base", provider="openrouter")
            agent.clear_conversation(user_id)

            return Response({"message": "Conversation cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error('error', exc_info=e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
