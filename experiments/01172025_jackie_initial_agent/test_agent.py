from utils.agent import TravelAgent
from utils.llm import ChatGPT
import uuid

# Initialize the TravelAgent with the OpenAI API key
llm = ChatGPT()
session_id = uuid.uuid4()

# Define test cases for the TravelAgent
test_inputs = [
    "testing",
    "Can you find me a flight from Boston to Los Angeles?",
    "Sure! I'm interested in flying on Feburary 2",  # Should result in a conversational response
]

# Loop through test cases and get responses
for i, user_input in enumerate(test_inputs, 1):

    travel_agent = TravelAgent(llm, session_id)

    print(f"\nTest Case {i}: {user_input}")
    response = travel_agent.process_user_input(user_input)
    print(f"Response: {response}")