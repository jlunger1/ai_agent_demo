from utils.registry import ToolRegistry
from travel_agent.core.models import Conversation, ConversationMessage, ToolMethod


class TravelAgent:
    def __init__(self, llm, session_id):
        self.llm = llm
        self.session_id = session_id
        self.tool_registry = ToolRegistry().get_tool_registry()
        self.conversation = self._get_or_create_conversation()
        self.conversation_history = self._load_conversation_history()
        self.system_prompt = self._generate_system_prompt()

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
        Save a message to the conversation.
        """
        return ConversationMessage.objects.create(
            conversation=self.conversation,
            sender=sender,
            content=content,
            tool=tool,
        )

    def _generate_system_prompt(self):
        """
        Generate a system prompt dynamically with the tool registry.
        """
        tool_descriptions = "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.tool_registry.items()]
        )
        return f"""
        You are an advanced AI travel assistant named Spotradius. Your primary goal is to assist users 
        in planning and managing their travel in a seamless and engaging way.

        Tools available:
        {tool_descriptions}

        Use the tools thoughtfully to provide enhanced responses. If tool results are already available 
        in the conversation history, incorporate them naturally into your answers. Keep your answers concise
        and informative, and maintain a conversational tone throughout the interaction.
        """

    def identify_tool(self):
        """
        Determine if the user's input would benefit from using a tool.
        """
        prompt = f"""
        {self.system_prompt}

        Based on the conversation so far, determine if any of the available tools would help answer the user's latest query.
        Respond with a JSON object in the format:
        {{ "tool": "<tool_name>" }}
        If no tool is needed, respond with: {{}}
        Conversation so far: {self.conversation_history}
        """

        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        try:
            response = eval(response)  # Convert response string to dictionary
            return response.get("tool", None)
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing tool identification response: {e}")
            return None

    def use_tool(self, tool_name, query):
        """
        Use a tool, save its result, and return the result for integration into the response.
        """
        tool_info = self.tool_registry.get(tool_name)
        if not tool_info:
            return f"Error: Tool '{tool_name}' not found."

        tool_method = tool_info["method"]
        tool_result = tool_method(query)

        # Save tool result to the conversation
        tool_instance = ToolMethod.objects.filter(name=tool_name).first()
        self._save_message(
            sender="assistant",
            content=f"Tool result: {tool_result}",
            tool=tool_instance,
        )

        return tool_result

    def respond_conversationally(self, tool_result=None):
        """
        Generate a conversational response, optionally incorporating tool results.
        """
        prompt = f"""
        {self.system_prompt}

        Tool result: {tool_result if tool_result else "None"}

        """

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

        # Decide whether a tool is needed
        tool_name = self.identify_tool()
        if tool_name:
            tool_result = self.use_tool(tool_name, query=user_input)
            # Incorporate tool result into the response
            return self.respond_conversationally(tool_result=tool_result)
        else:
            return self.respond_conversationally()