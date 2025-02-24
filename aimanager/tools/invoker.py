import json


def parse_llm_response(response_text: str):
    """
    Attempt to parse the LLM response as JSON.
    If it contains a 'function' key and 'parameters', assume it is a function call.
    Otherwise, return the text response.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Not valid JSON; treat as plain text.
        return {"type": "text", "content": response_text}

    if isinstance(data, dict) and "function" in data and "parameters" in data:
        return {"type": "function", "name": data["function"], "parameters": data["parameters"]}
    return {"type": "text", "content": response_text}


def trigger_function(call_request: dict, functions_registry: dict):
    """
    Call the function specified in the call_request.
    Supports both:
      - Positional arguments (passed in a list under "args")
      - Keyword arguments (passed in a dict under "kwargs" or as flat dict)
    """
    func_name = call_request["name"]
    params = call_request["parameters"]

    # Check if the parameters are structured into "args" and "kwargs".
    if isinstance(params, dict) and ("args" in params or "kwargs" in params):
        args = params.get("args", [])
        kwargs = params.get("kwargs", {})
    else:
        # Assume the parameters dict is just keyword arguments.
        args = []
        kwargs = params

    if func_name not in functions_registry:
        raise ValueError(f"Unknown function: {func_name}")

    func, defaults = functions_registry[func_name]
    return func(*args, **{**defaults, **kwargs})
