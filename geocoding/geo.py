from typing import List

import openrouteservice
from openrouteservice import convert
from openrouteservice.directions import directions
from openrouteservice.geocode import pelias_autocomplete

client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d79dd57e9e584a28a2f79c2d5bf6857e"
)  # Specify your personal API key
coords = [[37.704547, 55.802432], [37.675002, 55.773763]]


async def get_route_from_coords(coords: List[List[float]], profile="driving-car"):
    geometry = directions(client, coords, profile=profile)["routes"][0]["geometry"]
    decoded = convert.decode_polyline(geometry).get("coordinates")
    return decoded


async def suggest(query: str) -> list[str]:
    results = []

    try:
        routes = pelias_autocomplete(client, query, country="RUS", layers=["address"])
        for i in range(10):
            result = routes.get("features")[i].get("properties").get("name")
            results.append(result)
    except Exception as ex:
        print(ex)
    return results
