from utils.registry import ToolRegistry

tr = ToolRegistry()
validation_errors = tr.validate_registry()
print('validation errors:', validation_errors)

registry = tr.get_tool_registry()
print('registry:', registry)
