from utils.registry import ToolRegistry
from travel_agent.core.models import Conversation, ConversationMessage, ToolMethod


class TravelAgent:
    def __init__(self, llm, session_id):
        self.llm = llm
        self.session_id = session_id
        self.tool_registry = ToolRegistry().get_tool_registry()

        # Dynamically include the tool registry in the system prompt
        tool_registry_descriptions = "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.tool_registry.items()]
        )
        self.system_prompt = f"""
            You are an advanced AI travel assistant named Spotradius. Your primary goal is to help users plan and manage their travel in a seamless and engaging way. Here are your key responsibilities:

            1. **User Assistance**:
            - Provide thoughtful, friendly, and personalized answers to travel-related queries.
            - Offer creative suggestions for destinations, activities, and travel itineraries, even when the user query is vague.
            - Maintain a conversational and approachable tone, as if you are speaking to a friend.

            2. **Tool Usage**:
            - You have access to specialized tools that can perform tasks like searching for flights. These tools are described below:
                {tool_registry_descriptions}
            - Use tools only when their descriptions closely match the user's query.
            - When using a tool:
                - Extract the required parameters from the conversation so far.
                - If any parameters are missing, politely and conversationally ask the user for clarification.
                - Incorporate the tool results into a user-friendly summary that enhances the conversation.

            3. **Proactive Suggestions**:
            - If no tool is applicable, respond conversationally by offering relevant suggestions, asking clarifying questions, or helping the user brainstorm travel ideas.
            - Provide clear next steps to guide the user toward their travel goals.

            4. **Context Awareness**:
            - Remember the context of the conversation and reference past messages to maintain continuity.
            - If the user switches topics, gracefully adapt to the new topic without losing the conversational flow.

            5. **Fallback Behavior**:
            - If you are unsure how to answer or the user’s query is unclear, ask thoughtful clarifying questions to better understand their needs.
            - Avoid providing incomplete or generic responses—always aim to be specific and actionable.

            Tone: Be friendly, professional, and empathetic. Your goal is to make the user feel understood and supported in their travel planning.
        """

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

    def decide_action(self):
        """
        Dynamically decide whether to respond conversationally or use a tool.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Conversation so far:\n{self.conversation_history}\n\n"
            f"Based on the user's most recent message, decide whether to:\n"
            f"1. Respond conversationally.\n"
            f"2. Use a tool to gather or process information.\n"
            f"Respond with a JSON object:\n"
            f'{{ "action": "respond" }} or {{ "action": "use_tool", "tool": "<tool_name>" }}.'
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        return eval(response)  # Convert to a dictionary

    def extract_parameters(self, tool_name):
        """
        Extract required parameters for the specified tool from the conversation.
        """
        tool_info = self.tool_registry.get(tool_name)
        if not tool_info:
            return {"error": f"Tool '{tool_name}' not found."}

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Tool to use: {tool_name}\n"
            f"Description: {tool_info['description']}\n"
            f"The required parameters for this tool are:\n"
        )
        for param, desc in tool_info["parameters"].items():
            prompt += f"- {param}: {desc}\n"

        prompt += (
            "\nExtract the required parameters from the conversation so far. If any are missing, "
            "return a JSON object:\n"
            '{"missing_parameters": ["parameter1", "parameter2", ...]}. '
            "If all are available, return:\n"
            '{"parameters": {"parameter1": "value1", "parameter2": "value2", ...}}.'
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        return eval(response)  # Parsed as a dictionary

    def extract_parameters_conversationally(self, missing_parameters):
        """
        Generate a conversational message asking the user for missing parameters.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Conversation so far:\n{self.conversation_history}\n\n"
            f"The following parameters are missing:\n"
            + "\n".join(f"- {param}" for param in missing_parameters)
            + "\n\nCompose a friendly message asking the user for these missing details."
        )

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
        )

        self._save_message(sender="assistant", content=response)
        return response

    def use_tool(self, tool_name, parameters):
        """
        Execute the tool with the given parameters.
        """
        tool_info = self.tool_registry.get(tool_name)
        if not tool_info:
            return f"Error: Tool '{tool_name}' not found."

        tool_method = tool_info["method"]
        tool_result = tool_method(**parameters)

        # Save the tool output in the conversation
        tool_instance = ToolMethod.objects.filter(name=tool_name).first()
        self._save_message(
            sender="assistant",
            content=f"Tool result: {str(tool_result)[:100]}",  # Shortened for debugging
            tool=tool_instance,
        )

        return tool_result

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

        # Decide the next action
        action = self.decide_action()

        if action["action"] == "use_tool":
            tool_name = action.get("tool")
            if not tool_name:
                return "Error: Tool name missing from action."

            parameter_response = self.extract_parameters(tool_name)

            if "missing_parameters" in parameter_response:
                missing_message = self.extract_parameters_conversationally(
                    parameter_response["missing_parameters"]
                )
                return missing_message

            parameters = parameter_response.get("parameters", {})
            return self.use_tool(tool_name, parameters)

        return self.respond_conversationally()


class TravelAgentOld:
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
        tool_descriptions = "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.tool_registry.items()]
        )
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Available tools with their descriptions:\n"
            f"{tool_descriptions}\n\n"
            f"Based on the user's most recent message and the conversation so far, "
            f"determine if one of these tools should be used. Select a tool only if its description "
            f"closely matches the user's query. If no tool is applicable, return an empty JSON object: {{}}.\n\n"
            f"Respond with a JSON object in the format:\n"
            f'{{ "tool": "<tool_name>" }} or {{}}.\n\n'
            f"Conversation:\n{self.conversation_history}"
        )

        # Query the LLM for the decision
        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        try:
            response = eval(response)  # Convert response string to a dictionary
            return response.get("tool", None)
        except (SyntaxError, ValueError) as e:
            # Log the error and fallback to no tool selected
            print(f"Error parsing response: {e}")
            return None


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

