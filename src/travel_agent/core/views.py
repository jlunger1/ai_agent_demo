from django.http import JsonResponse
from tools.amadeus import AmadeusTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Amadeus tool
amadeus_tool = AmadeusTool(
    os.getenv("AMADEUS_API_KEY"),
    os.getenv("AMADEUS_API_SECRET")
)

def index(request):
    return JsonResponse({"message": "Welcome to the Travel Agent API"})

# Define the query processing view
def process_query(request):

    if request.method == "POST":
        import json
        body = json.loads(request.body)
        query = body.get("query", "")

        # Use the Amadeus tool to process the query
        response = amadeus_tool.search_flights("BOS", "LAX", "2025-02-01")
        return JsonResponse({"response": response})

    return JsonResponse({"error": "Invalid request method"}, status=405)
