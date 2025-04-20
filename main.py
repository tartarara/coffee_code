import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)

def main():
    apikey = os.getenv('GEOCODER_APIKEY')

    user_location = input("Где вы находитесь? ")
    coords = fetch_coordinates(apikey, user_location)

    with open("coffee.json", "r", encoding="CP1251") as coffee_file:
        coffee_data = json.load(coffee_file)

    coffee_shops = []

    for coffee in coffee_data:
        coffee_name = coffee["Name"]
        coffee_coords = coffee["geoData"]["coordinates"]
        coffee_lat, coffee_lon = coffee_coords[1], coffee_coords[0]

        dist = distance.distance((coffee_lat, coffee_lon), coords).km

        coffee_shops.append({
            "title": coffee_name,
            "distance": dist,
            "latitude": coffee_lat,
            "longitude": coffee_lon
        })

    sorted_coffee_shops = sorted(coffee_shops, key=lambda x: x['distance'])

    m = folium.Map(coords, zoom_start=16)
    for cafe in sorted_coffee_shops[:5]:
        cafe_title = cafe["title"]
        cafe_lat = cafe["latitude"]
        cafe_long = cafe["longitude"]
        folium.Marker(
            location=[cafe_lat, cafe_long],
            popup=f'<i>{cafe_title}</i>',
            tooltip=cafe_title
        ).add_to(m)

        m.save("index.html")

if __name__ == "__main__":
    main()
