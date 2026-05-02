"""
Module: booth.py
Description: Polling booth discovery routes for Chunav Mitra.
Author: Chunav Mitra Team
Version: 1.0.0
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import BoothRequest, BoothResponse
from app.services.maps_service import find_nearest_booth
from app.utils.logger import get_logger
from app.utils.validators import validate_pincode

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["booth"])


@router.post("/find-booth", response_model=BoothResponse)
async def find_booth(req: BoothRequest) -> BoothResponse:
    """Find a likely polling booth from pincode or GPS coordinates."""
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
