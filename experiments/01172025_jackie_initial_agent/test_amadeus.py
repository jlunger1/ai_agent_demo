import os
from travel_agent.tools.amadeus import AmadeusTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Amadeus tool
amadeus_tool = AmadeusTool(
    os.getenv("AMADEUS_API_KEY"),
    os.getenv("AMADEUS_API_SECRET")
)

# Test querying the Amadeus API
def test_amadeus_search():
    query = "Find flights from Boston to LA"  # Example query

    try:
        # Simulate the Amadeus tool's search method
        response = amadeus_tool.search_flights(origin="BOS", destination="LAX", departure_date="2025-02-01")
        print("API Response:", response)
    except Exception as e:
        print("Error during Amadeus API call:", e)


if __name__ == "__main__":
    test_amadeus_search()
