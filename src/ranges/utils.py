import requests
from requests import Session


def fetch(url: str, session: Session | None = None) -> str:
    if session is None:
        response = requests.get(url)
    else:
        response = session.get(url)

    response.raise_for_status()
    return response.text
