import googlemaps
from app.config import get_settings

settings = get_settings()

def _client():
    return googlemaps.Client(key=settings.google_maps_api_key)

def find_nearest_booth(pincode: str = None, lat: float = None, lng: float = None) -> dict:
    """Find nearest polling booth — returns dict with booth info or error key"""
    gmaps = _client()

    # Resolve pincode to coordinates
    if pincode and not lat:
        geocode = gmaps.geocode(f"{pincode}, India")
        if not geocode:
            return {"error": f"Pincode {pincode} nahi mila. Dobara check karein."}
        loc = geocode[0]["geometry"]["location"]
        lat, lng = loc["lat"], loc["lng"]

    if not lat:
        return {"error": "Location ya pincode dono nahi diye."}

    # Search polling booths
    places = gmaps.places_nearby(
        location=(lat, lng),
        radius=3000,
        keyword="polling booth election booth"
    )

    # Fallback to govt schools (common booth locations in India)
    if not places.get("results"):
        places = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,
            keyword="government school sarkari school"
        )

    if not places.get("results"):
        return {"error": "Koi booth nahi mila 3km mein. Apna pincode check karein."}

    booth = places["results"][0]
    b_lat = booth["geometry"]["location"]["lat"]
    b_lng = booth["geometry"]["location"]["lng"]

    # Get driving distance
    dist_matrix = gmaps.distance_matrix(
        origins=[(lat, lng)],
        destinations=[(b_lat, b_lng)],
        mode="driving"
    )
    distance_text = (
        dist_matrix["rows"][0]["elements"][0]
        .get("distance", {})
        .get("text", "Unknown distance")
    )

    return {
        "booth_name": booth.get("name", "Polling Booth"),
        "address": booth.get("vicinity", ""),
        "distance": distance_text,
        "maps_link": f"https://maps.google.com/?q={b_lat},{b_lng}",
        "lat": b_lat,
        "lng": b_lng,
    }
