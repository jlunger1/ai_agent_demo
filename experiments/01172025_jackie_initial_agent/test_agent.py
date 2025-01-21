from agent.agent import TravelAgent
from agent.tools.llm import GPT3_5

# Initialize the TravelAgent with the OpenAI API key
llm = GPT3_5()
travel_agent = TravelAgent(llm)

# Define test cases for the TravelAgent
test_inputs = [
    "testing"
    #"Can you find me a flight from Boston to Los Angeles on February 1st?",
    #"What's the best way to travel from New York to Paris?",
    #"I need a flight from Tokyo to Seoul on March 15th.",
    #"What’s the weather like in Boston today?",  # Should result in a conversational response
]

# Loop through test cases and get responses
for i, user_input in enumerate(test_inputs, 1):
    print(f"\nTest Case {i}: {user_input}")
    response = travel_agent.process_user_input(user_input)
    print(f"Response: {response}")

    break