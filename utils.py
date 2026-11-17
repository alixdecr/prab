import json
import requests
from pathlib import Path


# SERVER CHECK

def check_server(url: str, timeout: float = 5.0) -> dict:
    """
    Checks if a server URL responds.

    Args:
        url: Server URL.
        timeout: Seconds to wait per request.

    Returns:
        Dict with the server url, how it is hosted (local or online), if it is available, and the error name (if server is unavailable).
    """

    result = {"url": url, "hosted": "online", "available": False, "error": None}

    if "localhost" in url or url.startswith(("http://127.", "http://[::1]")):
        result["hosted"] = "local"
        result["available"] = True
        return result

    for request_method in (requests.head, requests.get):
        try:
            response = request_method(url, timeout=timeout, allow_redirects=True, stream=True)
            response.close()

            result["available"] = True
            result["error"] = None
            return result

        except Exception as e:
            result["available"] = False
            result["error"] = type(e).__name__

    return result


def is_server_available(server: dict) -> bool:
    """
    Checks if a server characteristics entry is considered available.
    Servers hosted locally are always considered available since they are not checked over the network.

    Args:
        server: Server dict from the API characteristics.

    Returns:
        True if the server is local or responded to a ping, False otherwise.
    """

    return server["hosted"] == "local" or server["available"]


# BADGE GENERATION

def generate_badge(label: str, message: str, color: str) -> str:
    """
    Generates a shields.io badge in Markdown format.

    Args:
        label: Left side of the badge.
        message: Right side of the badge.
        color: Color of the right side of the badge.

    Returns:
        Markdown of the badge.
    """

    label = label.replace("-", "--").replace(" ", "_").replace("%", "%25")
    message = message.replace("-", "--").replace(" ", "_").replace("%", "%25")

    return f"![alt text](https://img.shields.io/badge/{label}-{message}-{color}.svg)"


def get_percentage_color(percentage: float) -> str:
    """
    Picks a color based on a percentage value.

    Args:
        percentage: Percentage value between 0 and 100.

    Returns:
        Percentage color.
    """

    if percentage == 100:
        return "brightgreen"
    elif percentage >= 75:
        return "yellowgreen"
    elif percentage >= 50:
        return "orange"
    else:
        return "red"


# LOADING AND SAVING DATA

def load_json(path: Path) -> dict:
    """
    Loads JSON data from a file.

    Args:
        path: File path from where the JSON data is loaded.

    Returns:
        A dict of the loaded JSON data.
    """

    with open(path, mode="r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_json(path: Path, data: dict) -> None:
    """
    Saves data to a JSON file.

    Args:
        path: File path where the data is saved.
        data: Dict to be saved in the JSON file.
    """

    with open(path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_text(path: Path) -> str:
    """
    Loads text data from a file.
    
    Args:
        path: File path from where the text data is loaded.

    Returns:
        A string of the loaded text data.
    """

    with open(path, mode="r", encoding="utf-8") as file:
        return file.read()


def save_text(path: Path, data: str) -> None:
    """
    Saves string data to a file.
    
    Args:
        path: File path where the string data is saved.
        data: String to be saved in the file.
    """

    with open(path, mode="w", encoding="utf-8") as file:
        file.write(data)