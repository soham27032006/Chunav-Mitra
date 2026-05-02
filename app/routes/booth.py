"""
Module: booth.py
Purpose: Polling booth discovery routes for Chunav Mitra.
         Accepts a pincode or GPS coordinates, delegates to the maps service,
         and wraps results in a shaadi-analogy message about finding your mandap.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import BoothRequest, BoothResponse
from app.services.maps_service import find_nearest_booth
from app.utils.logger import get_logger
from app.utils.validators import validate_pincode

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["booth"])

__all__ = ["router", "find_booth"]


@router.post("/find-booth", response_model=BoothResponse)
async def find_booth(req: BoothRequest) -> BoothResponse:
    """Locate the nearest polling booth from a pincode or GPS coordinates.

    Accepts either a six-digit Indian pincode or a (lat, lng) coordinate
    pair. Delegates to the maps service which queries OpenStreetMap for
    government schools and official polling station nodes.

    Args:
        req: ``BoothRequest`` with ``pincode`` or ``lat``/``lng`` fields.

    Returns:
        ``BoothResponse`` with booth name, address, distance, maps link,
        and a shaadi-analogy message about finding your mandap.

    Raises:
        HTTPException: HTTP 400 when neither pincode nor GPS is supplied.
        HTTPException: HTTP 400 when the pincode format is invalid.
        HTTPException: HTTP 500 on unexpected server errors.

    Example:
        Request: ``{"pincode": "110001"}``
        Response: ``{"booth_name": "Polling Booth", "distance": "1.2 km", ...}``
    """
    try:
        if req.pincode:
            pincode = validate_pincode(req.pincode)
            result = find_nearest_booth(pincode=pincode)
        elif req.lat is not None and req.lng is not None:
            result = find_nearest_booth(lat=req.lat, lng=req.lng)
        else:
            raise HTTPException(
                status_code=400,
                detail="Pincode ya GPS location dono mein se ek chahiye.",
            )

        if "error" in result:
            return BoothResponse(
                booth_name="Booth not found",
                address="",
                distance="",
                maps_link="",
                message=str(result["error"]),
                lat=None,
                lng=None,
            )

        return BoothResponse(
            booth_name=str(result["booth_name"]),
            address=str(result["address"]),
            distance=str(result["distance"]),
            maps_link=str(result["maps_link"]),
            lat=float(result["lat"]) if result.get("lat") is not None else None,
            lng=float(result["lng"]) if result.get("lng") is not None else None,
            message=(
                f"Aapka mandap mil gaya. {result['booth_name']} lagbhag {result['distance']} door hai. "
                "Vote dene se pehle location ek baar map par confirm kar lijiye."
            ),
        )
    except HTTPException:
        raise
    except ValueError as error:
        logger.error("Booth validation error: %s", error)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.error("Error in booth endpoint: %s", error)
        raise HTTPException(
            status_code=500,
            detail="Kuch technical issue aa gaya. Please try again.",
        ) from error
