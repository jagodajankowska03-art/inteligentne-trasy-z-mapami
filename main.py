from flask import Flask, request
import requests
app = Flask(__name__)
# Geokodowanie adresu przez Nominatim
def geocode(adres):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": adres, "format": "json"}
    r = requests.get(url, params=params).json()
    if r:
        return float(r[0]["lat"]), float(r[0]["lon"])
    return None
# Algorytm najbliższego sąsiada
def nearest_neighbor(coords):
    if not coords:
        return []
    unvisited = coords[:]
    path = [unvisited.pop(0)]
    while unvisited:
        last = path[-1]
        next_point = min(unvisited, key=lambda x: (x[0]-last[0])**2 + (x[1]-last[1])**2)
        path.append(next_point)
        unvisited.remove(next_point)
    return path
# Podział adresów na 3 kierowców i optymalizacja tras
def podziel_trasy(adresy):
    coords_list = []
    for a in adresy:
        geo = geocode(a)
        if geo:
            coords_list.append((a, geo))
    kierowcy = {1: [], 2: [], 3: []}
    for i, item in enumerate(coords_list):
        kierowca = (i % 3) + 1
        kierowcy[kierowca].append(item)
    # optymalizacja tras
    for k in kierowcy:
        kierowcy[k] = nearest_neighbor(kierowcy[k])
    return kierowcy
@app.route("/", methods=["GET", "POST"])
def index():
    trasy = None
    if request.method == "POST":
        adresy = [a.strip() for a in request.form["adresy"].split("\n") if a.strip()]
        trasy = podziel_trasy(adresy)
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Inteligentne trasy 3 kierowców</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <style>#map { height: 600px; }</style>
    </head>
    <body>
        <h1>Inteligentne trasy 3 kierowców</h1>
        <form method="post">
            <textarea name="adresy" rows="10" cols="50" placeholder="Wpisz każdy adres w nowej linii"></textarea><br>
            <button type="submit">Generuj trasy</button>
        </form>
    """
    if trasy:
        html += '<div id="map"></div>'
        html += """
        <script>
            var map = L.map('map').setView([52.2297, 21.0122], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19
            }).addTo(map);
        """
        kolory = {1:"red", 2:"blue", 3:"green"}
        for k, punkty in trasy.items():
            if not punkty: continue
            latlngs = [[lat, lon] for _, (lat, lon) in punkty]
            html += f"L.polyline({latlngs}, {{color: '{kolory[k]}'}}).addTo(map);\n"
            for a, (lat, lon) in punkty:
                html += f"L.marker([{lat}, {lon}]).addTo(map).bindPopup('{a}');\n"
        html += "</script>"
    html += "</body></html>"
    return html
if __name__ == "__main__":
    app.run(debug=True)







