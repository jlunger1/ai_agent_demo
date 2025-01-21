from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from agent.agent import TravelAgent
from agent.tools.llm import GPT3_5


# Create your views here.
from django.http import JsonResponse
import json

@csrf_exempt
def ask(request):
    llm = GPT3_5()
    travel_agent = TravelAgent(llm)
    if request.method == "POST":

        body = json.loads(request.body)
        user_input = body.get("query", "")

        # Use the TravelAgent to process the input
        response = travel_agent.process_user_input(user_input)
        return JsonResponse({"message": response})

    return JsonResponse({"error": "Invalid request method"}, status=405)
