from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse
from aimanager.agent.builder import LLMAgentBuilder
import json

from apps.llmanager.permissions import IsAuthenticatedWithTrial

class ChatbotPromptView(APIView):
    permission_classes = [IsAuthenticatedWithTrial]

    def post(self, request):
        try:
            data = request.data
            prompt = data.get("prompt")

            if not prompt:
                return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)

            user_id = request.user.id if request.user.is_authenticated else request.ip_address

            agent = LLMAgentBuilder.build(agent_name="base")
            response_generator = agent.generate_response_stream(prompt, user_id)
            response = StreamingHttpResponse(response_generator, content_type="text/event-stream")
            response["Cache-Control"] = "no-cache"
            return response
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user_id = request.user.id if request.user.is_authenticated else request.ip_address

            agent = LLMAgentBuilder.build(agent_name="base", provider="openrouter")
            conversation = agent.get_conversation(user_id, system=False)

            return Response(conversation, status=status.HTTP_200_OK)
        except Exception as e:
            raise e
            # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            user_id = request.user.id if request.user.is_authenticated else request.ip_address

            agent = LLMAgentBuilder.build(agent_name="base", provider="openrouter")
            agent.clear_conversation(user_id)

            return Response({"message": "Conversation cleared"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
