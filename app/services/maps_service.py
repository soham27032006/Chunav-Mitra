"""
Module: maps_service.py
Description: Polling booth locator helpers for Chunav Mitra.
Uses open geocoding and OpenStreetMap sources to estimate nearby booths.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import Any

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests

from app.utils.logger import get_logger

logger = get_logger(__name__)
geolocator = Nominatim(user_agent="chunav_mitra_app")


def _format_result(
    booth_name: str,
    address: str,
    distance_km: str,
    maps_link: str,
    lat: float,
    lng: float,
) -> dict[str, Any]:
    """Build a normalized booth result payload.

    Args:
        booth_name: Human-readable booth or landmark name.
        address: Address string to display.
        distance_km: Distance string in kilometers.
        maps_link: Link to the location on a map.
        lat: Latitude coordinate.
        lng: Longitude coordinate.

    Returns:
        Normalized booth result dictionary.
    """
    return {
        "booth_name": booth_name,
        "address": address,
        "distance": distance_km,
        "maps_link": maps_link,
        "lat": lat,
        "lng": lng,
    }


def _query_overpass(lat: float, lng: float, query: str) -> dict[str, Any] | None:
    """Execute an Overpass query and return the first element.

    Args:
        lat: Latitude to search around.
        lng: Longitude to search around.
        query: Overpass query template.

    Returns:
        The first matching element, or ``None`` when nothing is found.

    Raises:
        requests.RequestException: When Overpass is unavailable.
    """
    response = requests.get(
        "https://overpass-api.de/api/interpreter",
        params={"data": query},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    elements = data.get("elements", [])
    if not elements:
        return None
    return elements[0]


def _build_booth_from_element(
    source_lat: float,
    source_lng: float,
    element: dict[str, Any],
    fallback_name: str,
) -> dict[str, Any]:
    """Convert an Overpass result into a booth payload.

    Args:
        source_lat: User latitude.
        source_lng: User longitude.
        element: Overpass element payload.
        fallback_name: Name to use if the element has no tag name.

    Returns:
        Normalized booth result dictionary.
    """
    booth_lat = float(element["lat"])
    booth_lng = float(element["lon"])
    name = element.get("tags", {}).get("name", fallback_name)
    address = element.get("tags", {}).get("addr:full", "")
    distance = round(geodesic((source_lat, source_lng), (booth_lat, booth_lng)).km, 2)
    return _format_result(
        booth_name=name,
        address=address,
        distance_km=f"{distance} km",
        maps_link=f"https://www.openstreetmap.org/?mlat={booth_lat}&mlon={booth_lng}",
        lat=booth_lat,
        lng=booth_lng,
    )


def _resolve_coordinates_from_pincode(pincode: str) -> tuple[float, float] | None:
    """Resolve a pincode into latitude and longitude.

    Args:
        pincode: Six-digit Indian pincode.

    Returns:
        Latitude and longitude tuple when resolution succeeds, else ``None``.
    """
    try:
        location = geolocator.geocode(f"{pincode}, India")
    except Exception as error:
        logger.warning("Pincode geocoding failed for %s: %s", pincode, error)
        return None

    if not location:
        return None
    return float(location.latitude), float(location.longitude)


def find_nearest_booth(
    pincode: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
) -> dict[str, Any]:
    """Find the nearest polling booth or likely polling location.

    Args:
        pincode: Optional Indian pincode.
        lat: Optional latitude from device geolocation.
        lng: Optional longitude from device geolocation.

    Returns:
        A normalized booth payload or an ``{"error": ...}`` result.

    Raises:
        ValueError: When both pincode and coordinates are missing.

    Example:
        >>> find_nearest_booth(pincode="110001")
        {'booth_name': 'Polling Booth', 'address': '...', 'distance': '1.2 km', ...}
    """
    if pincode and (lat is None or lng is None):
        coordinates = _resolve_coordinates_from_pincode(pincode)
        if not coordinates:
            return {"error": f"Pincode {pincode} could not be resolved."}
        lat, lng = coordinates

    if lat is None or lng is None:
        raise ValueError("Pincode or GPS coordinates are required.")

    booth_query = f"""
    [out:json][timeout:10];
    node["amenity"="polling_station"](around:5000,{lat},{lng});
    out body 1;
    """
    school_query = f"""
    [out:json][timeout:10];
    node["amenity"="school"]["operator:type"="government"](around:3000,{lat},{lng});
    out body 1;
    """

    try:
        element = _query_overpass(lat, lng, booth_query)
        if element:
            return _build_booth_from_element(lat, lng, element, "Polling Booth")
    except Exception as error:
        logger.warning("Polling booth lookup failed: %s", error)

    try:
        element = _query_overpass(lat, lng, school_query)
        if element:
            result = _build_booth_from_element(lat, lng, element, "Government School")
            result["booth_name"] = f"{result['booth_name']} (Likely Booth)"
            return result
    except Exception as error:
        logger.warning("Fallback school lookup failed: %s", error)

    try:
        reverse_location = geolocator.reverse(f"{lat}, {lng}", timeout=5)
        return _format_result(
            booth_name="Polling Booth (Verify exact location on ECI website)",
            address=reverse_location.address if reverse_location else f"{lat}, {lng}",
            distance_km="Unknown",
            maps_link=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}",
            lat=lat,
            lng=lng,
        )
    except Exception as error:
        logger.warning("Reverse geocoding fallback failed: %s", error)
        return _format_result(
            booth_name="Polling Booth",
            address="",
            distance_km="Unknown",
            maps_link=f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}",
            lat=lat,
            lng=lng,
        )
