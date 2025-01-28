from utils.agent import TravelAgent
from utils.llm import ChatGPT
import uuid

# Initialize the TravelAgent with the OpenAI API key
llm = ChatGPT()
session_id = uuid.uuid4()

# Define test cases for the TravelAgent
test_inputs = [
    "testing",
    "I'm looking for fun things to do in Boston",
    "What is our conversation history?"]

# Loop through test cases and get responses
for i, user_input in enumerate(test_inputs, 1):

    travel_agent = TravelAgent(llm, session_id)

    print(f"\nTest Case {i}: {user_input}")
    response = travel_agent.process_user_input(user_input)
    print(f"Response: {response}")