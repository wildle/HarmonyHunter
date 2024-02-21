import requests

def get_song_metadata(title):
    # Suche nach dem Songtitel mit DuckDuckGo
    query = f"{title} artist album year of publication"
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    
    # Überprüfe, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()
        # Extrahiere relevante Informationen aus der Antwort
        try:
            artist = data['AbstractText']
            album = data['AbstractSource']
            year = data['Year']
            return artist, album, year
        except KeyError:
            return None, None, None
    else:
        return None, None, None