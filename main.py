from flask import Flask, render_template, request, jsonify
import sqlite3
import folium
import json
import requests
app = Flask(__name__)
DB_PATH = 'db/debiut.db'
CACHE_FILE = 'cache.json'
# Wczytanie cache współrzędnych
try:
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
except:
    cache = {}
def geocode(adres):
    if adres in cache:
        return cache[adres]
    url = f"https://nominatim.openstreetmap.org/search?q={adres}&format=json"
    try:
        response = requests.get(url, timeout=5)
        r = response.json()
    except (ValueError, requests.exceptions.RequestException):
        r = []
    if r:
        lat = float(r[0]['lat'])
        lon = float(r[0]['lon'])
        cache[adres] = (lat, lon)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        return lat, lon
    return None, None  # brak wyników geokodowania
def get_clients():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nazwa, adres FROM Klienci")
    clients = c.fetchall()
    conn.close()
    return clients
@app.route("/", methods=['GET', 'POST'])
def index():
    map_html = None
    if request.method == 'POST':
        addresses = request.form.getlist('adres')
        coords = []
        for a in addresses:
            lat, lon = geocode(a)
            if lat is not None and lon is not None:
                coords.append((a, lat, lon))
        if coords:
            m = folium.Map(location=[coords[0][1], coords[0][2]], zoom_start=12)
            colors = ['red', 'blue', 'green']
            for i, (adres, lat, lon) in enumerate(coords):
                folium.Marker([lat, lon], popup=adres, icon=folium.Icon(color=colors[i%3])).add_to(m)
            map_html = m._repr_html_()
    return render_template('index.html', map_html=map_html)
if __name__ == "__main__":
    app.run(debug=True)












Jot something down

















