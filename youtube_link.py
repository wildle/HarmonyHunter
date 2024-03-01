import requests
from bs4 import BeautifulSoup

def get_youtube_link(title):
    """
    Sucht nach einem YouTube-Link für das angegebene Musikstücktitel.

    Args:
        title (str): Der Titel des Musikstücks.

    Returns:
        str oder None: Der gefunden YouTube-Link oder None, wenn kein Link gefunden wurde.
    """
    # Suchbegriffe für die YouTube-Suche erstellen
    keywords = f"{title} YouTube"

    # DuckDuckGo-Suchergebnisseite abrufen
    url = f"https://duckduckgo.com/html/?q={keywords}&kp=-2&ia=web"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')  # HTML-Seite parsen

        # Links auf der Seite finden
        links = soup.find_all('a', href=True)

        # Durch die Links iterieren und den ersten YouTube-Link zurückgeben
        for link in links:
            url = link['href']
            if 'youtube.com' in url:
                return url

    # Wenn keine Ergebnisse gefunden werden
    return None
