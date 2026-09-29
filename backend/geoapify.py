"""Credential-safe postcode resolution and nearby hotel discovery."""
from __future__ import annotations

from typing import Any
from datetime import datetime, timezone
import math
import re

import httpx

from .config import geoapify_api_key
from .models import ExternalHotel

GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
REQUEST_TIMEOUT_SECONDS = 10.0
PLACES_URL = "https://api.geoapify.com/v2/places"
SEARCH_RADIUS_METERS = 5000
RESULT_LIMIT = 100


class ZipLookupError(Exception):
    """Base exception whose message is safe to show to an API client."""


class MissingGeoapifyKeyError(ZipLookupError):
    """Raised when the backend does not have a usable Geoapify key."""


class ZipNotFoundError(ZipLookupError):
    """Raised when Geoapify cannot verify the requested U.S. postcode."""


class GeoapifyRequestError(ZipLookupError):
    """Raised for network, response, or payload failures from the provider."""


class GeoapifyRateLimitError(GeoapifyRequestError):
    """Raised when provider rate or credit limits prevent a search."""


def _valid_coordinates(result: dict[str, Any]) -> bool:
    latitude = result.get("lat")
    longitude = result.get("lon")
    return (
        isinstance(latitude, (int, float))
        and not isinstance(latitude, bool)
        and isinstance(longitude, (int, float))
        and not isinstance(longitude, bool)
        and math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def _location_from_result(result: dict[str, Any], postcode: str) -> dict[str, object] | None:
    """Return only a matching U.S. postcode result with usable coordinates."""
    if (
        str(result.get("postcode", "")).strip() != postcode
        or str(result.get("country_code", "")).strip().casefold() != "us"
        or not _valid_coordinates(result)
        or result.get("result_type", "postcode") != "postcode"
    ):
        return None

    locality = next(
        (
            str(result[field]).strip()
            for field in ("city", "locality", "name")
            if result.get(field) and str(result[field]).strip()
        ),
        None,
    )
    return {
        "postcode": postcode,
        "country_code": "us",
        "latitude": result["lat"],
        "longitude": result["lon"],
        "locality": locality,
    }


def lookup_us_zip(zip_code: str) -> dict[str, object]:
    """Resolve one five-digit U.S. ZIP code through Geoapify forward geocoding.

    A successful response contains only the verified postcode, country code,
    coordinates, and an available locality. Provider details and credentials
    intentionally never leave this controller.
    """
    postcode = zip_code.strip()
    if not re.fullmatch(r"[0-9]{5}", postcode):
        raise ZipNotFoundError("Enter a five-digit U.S. ZIP code.")

    api_key = geoapify_api_key()
    if not api_key:
        raise MissingGeoapifyKeyError("Geoapify API key is not configured.")

    payload = _request_json(
        GEOCODING_URL,
        {
                "postcode": postcode,
                "type": "postcode",
                "filter": "countrycode:us",
                "format": "json",
                "apiKey": api_key,
        },
    )

    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        raise GeoapifyRequestError("The location service returned an unexpected response.")

    for result in results:
        if isinstance(result, dict):
            location = _location_from_result(result, postcode)
            if location:
                return location
    raise ZipNotFoundError(f"No verified U.S. location was found for ZIP code {postcode}.")


def _request_json(url: str, params: dict) -> dict:
    """Never include upstream URLs, response bodies or keys in public errors."""
    try:
        response = httpx.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 429:
            raise GeoapifyRateLimitError("The location service reached its request or credit limit. Please try again later.")
        if response.status_code in (401, 403):
            raise MissingGeoapifyKeyError("The location service could not authorize this request. Check the backend API key configuration.")
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError, TypeError) as error:
        raise GeoapifyRequestError("The location service is unavailable. Please try again.") from error
    if not isinstance(payload, dict):
        raise GeoapifyRequestError("The location service returned an unexpected response.")
    return payload


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance from the returned ZIP point, not driving distance."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371008.8 * 2 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def search_hotels(zip_code: str) -> dict[str, Any]:
    center = lookup_us_zip(zip_code)
    lat, lon = center["latitude"], center["longitude"]
    payload = _request_json(PLACES_URL, {
        "categories": "accommodation.hotel",
        "filter": f"circle:{lon},{lat},{SEARCH_RADIUS_METERS}",
        "bias": f"proximity:{lon},{lat}",
        "limit": RESULT_LIMIT,
        "apiKey": geoapify_api_key(),
    })
    features = payload.get("features")
    if not isinstance(features, list):
        raise GeoapifyRequestError("The hotel service returned an unexpected response.")

    hotels, seen = [], set()
    skipped = 0
    for feature in features:
        props = feature.get("properties") if isinstance(feature, dict) else None
        if not isinstance(props, dict):
            skipped += 1
            continue
        place_id = _text(props.get("place_id"))
        coordinates = {"lat": props.get("lat"), "lon": props.get("lon")}
        if not _valid_coordinates(coordinates):
            geometry = feature.get("geometry")
            point = geometry.get("coordinates") if isinstance(geometry, dict) and geometry.get("type") == "Point" else None
            if isinstance(point, list) and len(point) >= 2:
                coordinates = {"lat": point[1], "lon": point[0]}
        if not place_id or not _valid_coordinates(coordinates):
            skipped += 1
            continue
        if place_id in seen:
            continue
        distance = distance_meters(lat, lon, coordinates["lat"], coordinates["lon"])
        if distance > SEARCH_RADIUS_METERS:
            skipped += 1
            continue
        name = _text(props.get("name"))
        address = _text(props.get("formatted"))
        if not address:
            address = ", ".join(filter(None, [_text(props.get("address_line1")), _text(props.get("address_line2"))])) or None
        hotels.append(ExternalHotel(
            place_id=place_id, name=name, address=address,
            latitude=coordinates["lat"], longitude=coordinates["lon"],
            distance_meters=round(distance, 1),
        ).model_dump())
        seen.add(place_id)
    if features and not hotels:
        raise GeoapifyRequestError("The hotel service returned records without usable locations inside the search area. Please try again.")
    hotels.sort(key=lambda hotel: (hotel["distance_meters"], hotel["place_id"]))
    return {
        "center": center,
        "hotels": hotels,
        "count": len(hotels),
        "radius_meters": SEARCH_RADIUS_METERS,
        "result_limit": RESULT_LIMIT,
        "limit_reached": len(features) >= RESULT_LIMIT,
        "omitted_records": skipped,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source": "Geoapify / OpenStreetMap",
    }
