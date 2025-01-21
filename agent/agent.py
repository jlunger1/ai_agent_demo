from agent.tools.registry import tool_registry

class TravelAgent:
    def __init__(self, llm):
        self.llm = llm
        self.conversation_history = []
        self.system_prompt = (
            "You are an AI travel assistant. Your job is to assist users with their travel needs by answering questions "
            "or using specialized tools when necessary. Always respond clearly and concisely."
        )

    def identify_tool(self):
        """
        Determine if the user's input would benefit from using a tool.
        """
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Available tools:\n"
            f"{tool_registry}\n\n"
            f"Based on the conversation so far, decide if one of these tools would help. "
            f"Respond with a JSON object in the format:\n"
            f'{{ "tool": tool chosen }}.\n\n'
            f'If no tool is needed, respond with an empty JSON object: {{}}.\n\n'
            f"Conversation:\n{self.conversation_history}"
        )

        # Use the enforced JSON response format
        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )
        # convert the response to a dictionary and return the tool name
        response = eval(response)
        return response.get("tool", None)

    def use_tool(self, tool_name):
        """
        Use the specified tool to handle the user's input.
        """
        tool_info = tool_registry.get(tool_name)
        if not tool_info:
            return f"Error: Tool '{tool_name}' not found."

        # Extract tool information
        parameters = tool_info["parameters"]
        parameter_format = tool_info.get("parameter_format", {})
        description = tool_info["description"]

        # LLM prompt to extract and format parameters
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Tool to use: {tool_name}\nDescription: {description}\n\n"
            f"The required parameters for this tool are:\n"
        )
        for param, format_description in parameter_format.items():
            prompt += f"- {param}: {format_description}\n"

        prompt += (
            "\nBased on the user's conversation so far, extract the required parameters "
            "in the correct format and respond with a JSON object. If any parameters are missing, "
            "please respond with a kind request for the missing information in this format: {'missing_parameters': request}."
        )

        # Query the LLM to extract parameters
        response = self.llm.query(
            prompt=prompt,
            conversation_history=self.conversation_history,
            response_format={"type": "json_object"},
        )

        response = eval(response)
        if "missing_parameters" in response:
            missing_message = response["missing_parameters"]
            return missing_message
        
        tool_method = tool_info["method"]
        tool_result = tool_method(**response)

        # Add result to conversation history and return it
        self.conversation_history.append({"role": "assistant", "content": f"Tool result: {tool_result}"})
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
            response_format=None,  # Regular conversational response
        )

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def process_user_input(self, user_input):
        """
        Main method to process user input and determine the appropriate response.
        """
        self.conversation_history.append({"role": "user", "content": user_input})

        tool_name = self.identify_tool()
        if tool_name:
            return self.use_tool(tool_name)
        else:
            return self.respond_conversationally()
