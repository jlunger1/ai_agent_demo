from dotenv import load_dotenv
load_dotenv()
import django
django.setup()

from travel_agent.core.models import ToolMethod
from utils.tools import AmadeusTool


class ToolRegistry:
    def __init__(self):
        # Initialize tool class instances
        self.tool_instances = {
            "AmadeusTool": AmadeusTool(),
        }
        self.registry = {}

    def validate_registry(self):
        """
        Validate that the ToolMethod objects in the database align with the tool_instances.
        """
        validation_errors = []

        for method in ToolMethod.objects.all():
            # Check if the tool_class exists in tool_instances
            if method.tool_class not in self.tool_instances:
                validation_errors.append(
                    f"Tool class '{method.tool_class}' for method '{method.name}' is not defined."
                )
                continue

            # Check if the method exists in the tool class instance
            tool_class_instance = self.tool_instances[method.tool_class]
            if not hasattr(tool_class_instance, method.name):
                validation_errors.append(
                    f"Method '{method.name}' is not defined in tool class '{method.tool_class}'."
                )

        return validation_errors

    def load_registry(self):
        """
        Dynamically populate the tool registry from the database, ensuring all entries are valid.
        """
        self.registry.clear()  # Clear the registry to reload

        # Perform validation
        validation_errors = self.validate_registry()
        if validation_errors:
            raise ValueError(f"Tool registry validation errors: {', '.join(validation_errors)}")

        # Populate the registry
        for method in ToolMethod.objects.all():
            tool_class_instance = self.tool_instances.get(method.tool_class)
            if tool_class_instance:
                self.registry[method.name] = {
                    "method": getattr(tool_class_instance, method.name, None),
                    "parameters": method.parameters,
                    "description": method.description,
                }

    def get_tool_registry(self):
        """
        Return the current tool registry.
        """
        if not self.registry:  # Ensure the registry is loaded
            self.load_registry()
        return self.registry
