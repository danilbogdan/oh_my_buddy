import httpx

from aimanager.tools.scheme import llm_tool


@llm_tool
async def fetch_weather_async(location):
    """
    Fetch weather data from the OpenWeatherMap API asynchronously.

    :param location: The location for which to fetch the weather.
    :param api_key: The API key for authentication.
    :return: A dictionary containing the weather data.
    """
    api_key = "45a13c844a14ea8cd31bcb2782455b78"
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key}
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        response.raise_for_status()
        return response.json()


@llm_tool
def fetch_weather_sync(location):
    """
    Fetch weather data from the OpenWeatherMap API synchronously.

    :param location: The location for which to fetch the weather.
    :param api_key: The API key for authentication.
    :return: A dictionary containing the weather data.
    """
    api_key = "45a13c844a14ea8cd31bcb2782455b78"
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key}
    with httpx.Client() as client:
        response = client.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
