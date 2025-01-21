from amadeus import Client, ResponseError
import os
import json
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_API_SECRET")

class AmadeusTool:
    def __init__(self):
        self.client = Client(client_id=api_key, client_secret=api_secret)

    def search_flights(self, origin, destination, departure_date, adults=1):
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults
            )
            return json.dumps(response.data, indent=2)
        except ResponseError as error:
            return {"error": str(error)}
