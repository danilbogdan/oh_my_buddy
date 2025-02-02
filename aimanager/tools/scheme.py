import inspect
from typing import Callable, Optional, Union


def llm_tool(description_or_func: Optional[Union[str, Callable]] = None):
    """
    Decorator to attach an LLM-compatible JSON schema describing the function.
    Can be used as @llm_tool or @llm_tool(description).
    """
    # If decorator is used without parameters
    if callable(description_or_func):
        return _create_schema_wrapper(description_or_func, None)

    # If decorator is used with parameters
    def decorator(func):
        return _create_schema_wrapper(func, description_or_func)

    return decorator


def _create_schema_wrapper(func: Callable, description: Optional[str]):
    sig = inspect.signature(func)
    properties = {}
    required = []
    allow_additional = False  # Will be True if **kwargs is present

    for name, param in sig.parameters.items():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            # *args: document as an array parameter.
            properties[name] = {
                "type": "array",
                "items": {"type": "string"},
                "description": f"{name} (positional arguments)",
            }
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            # **kwargs: allow additional properties.
            allow_additional = True
        else:
            param_schema = {}
            ann = param.annotation
            if ann is not inspect.Parameter.empty:
                if ann == int:
                    param_schema["type"] = "integer"
                elif ann == float:
                    param_schema["type"] = "number"
                elif ann == bool:
                    param_schema["type"] = "boolean"
                elif ann == list:
                    param_schema["type"] = "array"
                elif ann == dict:
                    param_schema["type"] = "object"
                else:
                    param_schema["type"] = "string"
            else:
                param_schema["type"] = "string"
            param_schema["description"] = f"{name} parameter"
            properties[name] = param_schema

            if param.default is inspect.Parameter.empty:
                required.append(name)

    parameters_schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": allow_additional,
    }

    if not (description or func.__doc__):
        raise TypeError("description or docstring required")

    function_schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description or (func.__doc__ or "No description provided."),
            "parameters": parameters_schema,
            "strict": not allow_additional,
        },
    }
    func.llm_schema = function_schema
    return func
