from utils.registry import ToolRegistry
from travel_agent.core.models import Conversation, ConversationMessage, ToolMethod
import json


class TravelAgent:
    def __init__(self, llm, session_id):
        self.llm = llm
        self.session_id = session_id
        self.system_prompt = (
            "You are an AI travel assistant. Your job is to assist users with their travel needs by answering questions "
            "or using specialized tools when necessary. Always respond clearly and concisely."
        )
        self.tool_registry = ToolRegistry().get_tool_registry()

        # Initialize or load the conversation
        self.conversation = self._get_or_create_conversation()
        self.conversation_history = self._load_conversation_history()

    def _get_or_create_conversation(self):
        """
        Retrieve or create a Conversation object based on the session_id.
        """
        conversation, _ = Conversation.objects.get_or_create(session_id=self.session_id)
        return conversation

    def _load_conversation_history(self):
        """
        Load the conversation history for the current session as a list of messages.
        """
        messages = self.conversation.messages.order_by("created_at")
        return [{"role": msg.sender, "content": msg.content} for msg in messages]

    def _save_message(self, sender, content, tool=None):
        """
        Save a message to the conversation in the database.
        """
        ConversationMessage.objects.create(
            conversation=self.conversation,
            sender=sender,
            content=content,
            tool=tool,
        )

    def identify_tool(self):
        """
        Determine if the user's input would benefit from using a tool.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Available tools:\n"
            f"{self.tool_registry}\n\n"
            f"Based on the conversation so far, decide if one of these tools would help. "
            f"Respond with a JSON object in the format:\n"
            f'{{ "tool": "<tool_name>" }}\n\n'
            f"If no tool is needed, respond with an empty JSON object: {{}}.\n\n"
            f"Conversation:\n{self.conversation_history}"
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )
        response = eval(response)
        return response.get("tool", None)

    def extract_parameters(self, tool_name):
        """
        Extract required parameters for the specified tool from the conversation.
        """
        tool_info = self.tool_registry.get(tool_name)
        if not tool_info:
            return {"error": f"Tool '{tool_name}' not found."}

        parameters = tool_info["parameters"]
        description = tool_info["description"]

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Tool to use: {tool_name}\nDescription: {description}\n\n"
            f"The required parameters for this tool are:\n"
        )
        for param, format_description in parameters.items():
            prompt += f"- {param}: {format_description}\n"

        prompt += (
            "\nBased on the user's conversation so far, extract the required parameters in the correct format "
            "and respond with a JSON object:\n"
            '{"extracted_parameters": {"parameter1": "value", ...}, "missing_parameters": ["parameter1", ...]}.\n\n'
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        return eval(response)  # Parsed as a dictionary

    def extract_parameters_conversationally(self, missing_parameters):
        """
        Use the LLM to generate a conversational response requesting missing parameters.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Conversation so far:\n{self.conversation_history}\n\n"
            f"The user has requested assistance with a task that requires the following information:\n"
        )
        for param in missing_parameters:
            prompt += f"- {param}\n"

        prompt += (
            "\nPlease compose a friendly, conversational response to the user. "
            "Your goal is to ask for the missing information clearly and politely, "
            "while maintaining the flow of the conversation."
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
        )

        self._save_message(sender="assistant", content=response)
        return response


    def use_tool(self, tool_name, parameters):
        """
        Use the specified tool with the given parameters.
        """
        tool_info = self.tool_registry.get(tool_name)
        if not tool_info:
            return f"Error: Tool '{tool_name}' not found."

        tool_method = tool_info["method"]
        tool_result = tool_method(**parameters)

        # Fetch the ToolMethod instance from the database
        tool_instance = ToolMethod.objects.filter(name=tool_name).first()

        # Save the tool result in the conversation history
        tool_result_summary = str(tool_result)[:100]  # Limit output to 100 characters for debugging
        self._save_message(sender="assistant", content=f"Tool result: {tool_result_summary}", tool=tool_instance)

        return tool_result_summary

    def respond_conversationally(self):
        """
        Generate a conversational response if no tool is required.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Conversation so far:\n{self.conversation_history}\n\n"
            f"Provide a helpful and natural response to the user's input."
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
        )

        self._save_message(sender="assistant", content=response)
        return response

    def process_user_input(self, user_input):
        """
        Main method to process user input and determine the appropriate response.
        """
        self._save_message(sender="user", content=user_input)
        self.conversation_history.append({"role": "user", "content": user_input})

        tool_name = self.identify_tool()
        if tool_name:
            parameter_response = self.extract_parameters(tool_name)

            if "missing_parameters" in parameter_response and parameter_response["missing_parameters"]:
                missing_message = self.extract_parameters_conversationally(
                    parameter_response["missing_parameters"]
                )
                return missing_message

            # Assume parameters are complete and use the tool
            parameters = parameter_response.get("extracted_parameters", {})
            return self.use_tool(tool_name, parameters)
        else:
            return self.respond_conversationally()

