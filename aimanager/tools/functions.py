import json
import httpx
import logging

from aimanager.tools.scheme import llm_tool

logger = logging.getLogger("django")


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


@llm_tool
async def list_files(
    count: int = 10,
    order_by: str = "name",
    order_direction: str = "asc",
    name_pattern: str = None,
    file_extension: str = None
) -> str:
    """
    Lists files in the /tmp/doc/ directory with various filtering options.
    Args:
        count (int): Maximum number of files to return. Default is 10.
        order_by (str): Field to order by. One of: 'name', 'size', 'modified'. Default is 'name'.
        order_direction (str): Order direction. One of: 'asc', 'desc'. Default is 'asc'.
        name_pattern (str): Pattern to match in file names. If None, no pattern matching is applied.
        file_extension (str): Filter by file extension (e.g., 'pdf', 'docx'). If None, all extensions are included.
    Returns:
        str: JSON string containing the list of files with their properties
    """
    import os
    from datetime import datetime
    import re
    logger.info(f"Listing files with parameters: count={count}, order_by={order_by}, order_direction={order_direction}, name_pattern={name_pattern}, file_extension={file_extension}")
    base_path = os.path.join(os.getenv("TMP_PATH"), "doc")
    if not os.path.exists(base_path):
        return "[]"

    files = []
    for filename in os.listdir(base_path):
        if file_extension and not filename.endswith(f".{file_extension}"):
            continue
        if name_pattern and not re.search(name_pattern, filename, re.IGNORECASE):
            continue

        file_path = os.path.join(base_path, filename)
        if os.path.isfile(file_path):
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": os.path.splitext(filename)[1][1:]
            })

    # Sort files
    reverse = order_direction.lower() == "desc"
    files.sort(key=lambda x: x[order_by], reverse=reverse)

    # Limit count
    files = files[:count]

    return json.dumps(files)


@llm_tool
async def rename_file(existing_name: str, new_name: str) -> str:
    """
    Renames a file in the /tmp/doc/ directory.
    Args:
        existing_name (str): Current name of the file
        new_name (str): New name for the file
    Returns:
        str: Success or error message
    """
    import os
    import shutil

    base_path = os.path.join(os.getenv("TMP_PATH"), "doc")
    old_path = os.path.join(base_path, existing_name)
    new_path = os.path.join(base_path, new_name)

    if not os.path.exists(old_path):
        return f"Error: File '{existing_name}' does not exist"
    
    if os.path.exists(new_path):
        return f"Error: File '{new_name}' already exists"

    try:
        shutil.move(old_path, new_path)
        return f"Successfully renamed '{existing_name}' to '{new_name}'"
    except Exception as e:
        return f"Error renaming file: {str(e)}"
