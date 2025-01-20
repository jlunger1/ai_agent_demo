from amadeus import Client, ResponseError

class AmadeusTool:
    def __init__(self, api_key, api_secret):
        self.client = Client(client_id=api_key, client_secret=api_secret)

    def search_flights(self, origin, destination, departure_date, adults=1):
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults
            )
            return response.data
        except ResponseError as error:
            return {"error": str(error)}
