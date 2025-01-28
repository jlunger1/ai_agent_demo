from amadeus import Client, ResponseError
import os
import json
from dotenv import load_dotenv
load_dotenv()
import requests


class AmadeusTool:
    def __init__(self):
        api_key = os.getenv("AMADEUS_API_KEY")
        api_secret = os.getenv("AMADEUS_API_SECRET")
        self.client = Client(client_id=api_key, client_secret=api_secret)

    def search_flights(self, origin, destination, departure_date, adults=1):
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults
            )
            response = json.dumps(response.data, indent=2)
            # append the origin, destination and departure date to the beginning of the response for debugging
            response = f"Origin: {origin}, Destination: {destination}, Departure Date: {departure_date}\n{response}"
            return response
        except ResponseError as error:
            return {"error": str(error)}

class GooglePlacesTool:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def search_places(self, query):
        """
        Use the Places API Text Search to find places based on a query string
        and return a formatted summary of results.
        :param query: Natural language search query (e.g., 'restaurants near Boston').
        :return: Formatted string with top results.
        """
        params = {
            "key": self.api_key,
            "query": query,
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        raw_data = response.json()

        return self._format_places_result(raw_data)

    def _format_places_result(self, raw_data):
        """
        Format the raw Google Places API result into a user-friendly summary.
        :param raw_data: Raw JSON response from the Places API.
        :return: Formatted string summary.
        """
        if not raw_data.get("results"):
            return "No results found for your query."

        formatted_places = []
        for place in raw_data["results"][:5]:  # Limit to top 5 results
            name = place.get("name", "Unknown Name")
            address = place.get("formatted_address", "Unknown Address")
            rating = place.get("rating", "No rating")
            user_ratings_total = place.get("user_ratings_total", 0)
            open_now = place.get("opening_hours", {}).get("open_now", False)
            open_status = "Open" if open_now else "Closed"
            types = ", ".join(place.get("types", []))

            # Format the output for each place
            formatted_places.append(
                f"- **{name}** (Rating: {rating}, {user_ratings_total} ratings)\n"
                f"  Address: {address}\n"
                f"  Open/Closed Status: {open_status}\n"
                f"  Type: {types}\n"
            )

        return "\n\n".join(formatted_places)