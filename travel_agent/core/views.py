from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from travel_agent.core.models import Conversation
from utils.agent import TravelAgent
from utils.llm import ChatGPT

from django.http import JsonResponse
import json
import uuid

@csrf_exempt
def start_session(request):
    """
    Start a new session and return the session_id to the client.
    """
    if request.method == "POST":
        # Generate a new session ID
        session_id = uuid.uuid4()
        
        # Create a new conversation in the database
        Conversation.objects.create(session_id=session_id)
        
        return JsonResponse({"session_id": str(session_id)}, status=201)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def ask(request):
    """
    Handle user queries and provide responses via the TravelAgent.
    """
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)
            user_input = body.get("query", "")
            session_id = body.get("session_id", None)

            if not user_input or not session_id:
                return JsonResponse({"error": "Both 'query' and 'session_id' are required."}, status=400)

            # Initialize LLM and TravelAgent
            llm = ChatGPT()
            travel_agent = TravelAgent(llm, session_id)

            # Use the TravelAgent to process the input
            response = travel_agent.process_user_input(user_input)
            return JsonResponse({"message": response}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON input."}, status=400)
        except Conversation.DoesNotExist:
            return JsonResponse({"error": "Invalid session_id."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)
