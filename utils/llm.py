import openai
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class ChatGPT:
    def __init__(self, model="gpt-4o"):
        """
        Initialize ChatGPT with the provided API key.
        """
        self.api_key = api_key
        openai.api_key = self.api_key

    def query(self, prompt, conversation_history=None, max_tokens=150, temperature=0.7, response_format=None):
        """
        Query GPT-3.5 with a prompt and optional conversation history.

        :param prompt: System-level instructions or task definition.
        :param conversation_history: List of conversation history messages.
        :param max_tokens: Maximum number of tokens in the output.
        :param temperature: Sampling temperature for diversity in responses.
        :param response_format: Dict to enforce specific response format (e.g., JSON object).
        :return: The response content as a string or structured JSON if response_format is specified.
        """
        # Combine prompt and conversation history
        messages = [{"role": "system", "content": prompt}]
        if conversation_history:
            messages.extend(conversation_history)

        # Call the OpenAI API
        if response_format:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,  # Use the response format
            )
        else:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        return response.choices[0].message.content