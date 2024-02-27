import requests
from bs4 import BeautifulSoup

def get_spotify_link(title):
    keywords = f"{title} Spotify"

    # DuckDuckGo-Suchergebnisseite abrufen
    url = f"https://duckduckgo.com/html/?q={keywords}&kp=-2&ia=web"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser') #Aufruf HTML Seite

        # Links auf der Seite finden
        links = soup.find_all('a', href=True)

        # Durch die Links iterieren und den ersten Spotify-Link zurückgeben
        for link in links:
            url = link['href']
            if 'spotify.com' in url:
                return url

    # Wenn keine Ergebnisse gefunden werden
    return None