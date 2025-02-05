from .base import env

OPENAI_CONFIG = {
    "API_KEY": env.str("OPENAI_API_KEY", default=""),
}
