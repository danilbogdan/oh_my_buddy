import asyncio
import json
import unittest

from aimanager.tools.invoker import parse_llm_response, trigger_function
from aimanager.tools.scheme import llm_tool


class TestLLMTool(unittest.TestCase):
    def test_decorator_with_description(self):
        @llm_tool("Test description")
        def func(x: int, y: str = "default"):
            """Function docstring"""
            return x, y

        schema = func.llm_schema
        self.assertEqual(schema["function"]["description"], "Test description")
        self.assertEqual(schema["function"]["name"], "func")
        self.assertTrue("x" in schema["function"]["parameters"]["required"])
        self.assertFalse("y" in schema["function"]["parameters"]["required"])

    def test_decorator_without_description(self):
        @llm_tool
        def func(x: int):
            """Test docstring"""
            return x

        schema = func.llm_schema
        self.assertEqual(schema["function"]["description"], "Test docstring")
        self.assertEqual(schema["function"]["name"], "func")

    def test_kwargs_handling(self):
        @llm_tool("Test with kwargs")
        def func(**kwargs):
            return kwargs

        schema = func.llm_schema
        self.assertTrue(schema["function"]["parameters"]["additionalProperties"])

    def test_direct_creation(self):
        def func(x: int):
            """Direct creation test"""
            return x

        wrapped = llm_tool()(func)
        self.assertTrue(hasattr(wrapped, "llm_schema"))
        self.assertEqual(wrapped.llm_schema["function"]["name"], "func")

    def test_missing_description_and_docstring(self):
        with self.assertRaises(TypeError):

            @llm_tool
            def func(x):
                pass


class TestInvoker(unittest.TestCase):
    def setUp(self):
        # Set up test functions
        @llm_tool("Test function")
        def test_func(x: int, y: str = "default"):
            return f"x={x}, y={y}"

        @llm_tool("Test async function")
        async def test_async_func(a: int, b: int = 0):
            await asyncio.sleep(0.1)
            return a + b

        self.registry = {test_func.__name__: test_func, test_async_func.__name__: test_async_func}

    def test_parse_valid_function_call(self):
        response = json.dumps({"function": "test_func", "parameters": {"x": 42}})
        result = parse_llm_response(response)
        self.assertEqual(result["type"], "function")
        self.assertEqual(result["name"], "test_func")
        self.assertEqual(result["parameters"], {"x": 42})

    def test_parse_text_response(self):
        response = "This is a plain text response"
        result = parse_llm_response(response)
        self.assertEqual(result["type"], "text")
        self.assertEqual(result["content"], response)

    def test_parse_invalid_json(self):
        response = "{invalid json}"
        result = parse_llm_response(response)
        self.assertEqual(result["type"], "text")
        self.assertEqual(result["content"], response)

    def test_trigger_sync_function(self):
        call_request = {"name": "test_func", "parameters": {"x": 42, "y": "test"}}
        result = trigger_function(call_request, self.registry)
        self.assertEqual(result, "x=42, y=test")

    def test_trigger_with_args_kwargs(self):
        call_request = {"name": "test_func", "parameters": {"args": [42], "kwargs": {"y": "test"}}}
        result = trigger_function(call_request, self.registry)
        self.assertEqual(result, "x=42, y=test")

    def test_trigger_async_function(self):
        call_request = {"name": "test_async_func", "parameters": {"a": 5, "b": 3}}
        result = asyncio.run(self.registry["test_async_func"](**call_request["parameters"]))
        self.assertEqual(result, 8)

    def test_unknown_function(self):
        call_request = {"name": "unknown_func", "parameters": {}}
        with self.assertRaises(ValueError):
            trigger_function(call_request, self.registry)

    def test_default_parameters(self):
        call_request = {"name": "test_func", "parameters": {"x": 42}}  # y has default value
        result = trigger_function(call_request, self.registry)
        self.assertEqual(result, "x=42, y=default")


if __name__ == "__main__":
    unittest.main()
