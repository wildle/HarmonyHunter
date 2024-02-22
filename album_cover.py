from duckduckgo_search import DDGS

def get_album_cover(title):
    # Suchbegriffe für die Albumcover-Suche
    keywords = f"{title} Albumcover"

    # Ergebnisse der Bildersuche abrufen
    with DDGS() as ddgs:
        ddgs_images_gen = ddgs.images(
            keywords,
            region="wt-wt",
            safesearch="off",
            size=None,
            color=None,
            type_image=None,
            layout=None,
            license_image=None,
            max_results=10,  # Anzahl der maximalen Ergebnisse
        )
        
        # Durch die Ergebnisse iterieren und die URL des ersten Bildes zurückgeben
        for result in ddgs_images_gen:
            return result['image']
    
    # Wenn keine Ergebnisse gefunden werden
    return None