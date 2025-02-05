The overall flow of handling user queries with function calls is as follows:

1. **User Input:**  
   The user sends a query (e.g., "What’s the weather like in Paris?").

2. **LLM Prompting:**  
   You send the user query to the LLM along with the instructions (`prompts.FUNCTION_INSTRUCTION`) and a description of available functions (generate scheme using `scheme.llm_tool`).  
   *The prompt could be composed by combining the system instructions, the function definitions, and the user query.*

3. **LLM Response:**  
   - **If a function call is appropriate:** The LLM returns a JSON object exactly matching the schema (for instance, a call to `get_weather` with a location parameter).  
   - **If a function call is not needed:** The LLM returns a text answer.

4. **Response Parsing and Handling:**  
   Your tool inspects the LLM response (`invoker.parse_llm_response`):
   - If it is plain text, you display it to the user.
   - If it’s a JSON object indicating a function call, you parse out the function name and parameters.

5. **Function Triggering:**  
   Using the parsed function name and parameters, you look up the corresponding function from your registered tools and execute it.  (`invoker.trigger_function`):
   - For asynchronous functions, you call them using an async event loop.
   - For synchronous functions, you call them normally.

6. **Result Integration:**  
   Once the function call returns a result, you can then feed that result back into the conversation. For example, you might send the function’s output back to the LLM with a message like “The result of the function call is: …”, or display it to the user.
