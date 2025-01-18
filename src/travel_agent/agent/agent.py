from tools.amadeus import AmadeusTool
from openai import ChatCompletion

class TravelAgent:
    def __init__(self, amadeus_tool, llm_api_key):
        self.amadeus = amadeus_tool
        self.llm = ChatCompletion(api_key=llm_api_key)

    def process_user_input(self, user_input):
        # Step 1: Use LLM to decide on the tool to invoke
        decision = self.llm.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI travel assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        # Step 2: Based on decision, invoke a tool (e.g., Amadeus)
        if "flight search" in decision["choices"][0]["message"]["content"]:
            return self.amadeus.search_flights("BOS", "LAX", "2025-02-01")
        else:
            return {"error": "I don't know how to handle that request yet."}
