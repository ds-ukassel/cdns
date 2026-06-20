from requests import Session


def fetch(session: Session, url: str) -> str:
    response = session.get(url)
    response.raise_for_status()
    return response.text
