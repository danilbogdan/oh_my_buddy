FUNCTION_INSTRUCTION = """
You can call external functions to fulfill user requests. When you believe that one of the available functions is needed to answer the user’s query, please respond with a JSON object that exactly matches the following format:

{
    "function": "<function_name>",
    "parameters": {
        "parameter1": value,
        "parameter2": value,
        ...
    }
}

Make sure:
- The JSON exactly follows the provided schema for that function.
- Do not include any extra text outside the JSON if you intend to call a function.
- If no function call is needed, you may answer directly in text.

For example, if get_weather function is available:

Input schame:
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "location parameter"
                }
            },
            "required": [
                "location"
            ],
            "additionalProperties": false
        },
        "strict": true
    }
}


Expected output
{
    "function": "get_weather",
    "parameters": {
         "location": "Paris, France"
    }
}

Use the function schemas strictly. For example, if you want to call `get_weather`, your response must contain only function schema and respons must be a valid json. It must not contain any text reply. Just function definition schema.
If you have all the required data - call function first, do not tell user about it.
If you decide that no function is required, simply provide your answer as text.

The following functions are available for you:
"""
