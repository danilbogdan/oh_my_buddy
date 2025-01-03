from .base import env

CUSTOM_OPENAI_HOST = env.str("CUSTOM_OPENAI_HOST", default="http://localhost")
CUSTOM_OPENAI_PORT = env.str("CUSTOM_OPENAI_PORT", default="1234")