# agent/tools/registry.py
from agent.tools.amadeus import AmadeusTool

# Initialize the tool
amadeus_tool = AmadeusTool()

# Tool registry
tool_registry = {
    "search_flights": {
        "method": amadeus_tool.search_flights,
        "parameters": ["origin", "destination", "departure_date"],
        "description": "Search for flights between two cities on a specific date.",
        "parameter_format": {
            "origin": "The IATA airport code for the departure location (e.g., BOS for Boston).",
            "destination": "The IATA airport code for the arrival location (e.g., LAX for Los Angeles).",
            "departure_date": "The departure date in YYYY-MM-DD format (e.g., 2025-02-01).",
        },
    }
}
