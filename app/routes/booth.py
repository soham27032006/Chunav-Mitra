from fastapi import APIRouter, HTTPException
from app.models.schemas import BoothRequest, BoothResponse
from app.services.maps_service import find_nearest_booth

router = APIRouter(prefix="/api", tags=["booth"])

@router.post("/find-booth", response_model=BoothResponse)
async def find_booth(req: BoothRequest):
    if not req.pincode and not (req.lat and req.lng):
        raise HTTPException(status_code=400, detail="Pincode ya GPS location dono mein se ek chahiye.")

    result = find_nearest_booth(pincode=req.pincode, lat=req.lat, lng=req.lng)

    if "error" in result:
        return BoothResponse(
            booth_name="Nahi mila",
            address="",
            distance="",
            maps_link="",
            message=result["error"],
        )

    return BoothResponse(
        booth_name=result["booth_name"],
        address=result["address"],
        distance=result["distance"],
        maps_link=result["maps_link"],
        message=(
            f"Aapka Mandap mil gaya! "
            f"'{result['booth_name']}' sirf {result['distance']} door hai. "
            f"Mehndi lagane ka time aa gaya — chalo vote dene!"
        ),
    )
