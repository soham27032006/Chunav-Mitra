from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class AskResponse(BaseModel):
    response: str
    detected_lang: str          # "hi" or "en"
    intent: str                 # "voter_check" | "booth_finder" | "timeline" | "general"
    session_id: Optional[str] = None

class VoterCheckRequest(BaseModel):
    name: str
    state: str
    dob: Optional[str] = None   # DD/MM/YYYY

class VoterCheckResponse(BaseModel):
    found: bool
    message: str                # shaadi analogy message
    voter_id: Optional[str] = None

class BoothRequest(BaseModel):
    pincode: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class BoothResponse(BaseModel):
    booth_name: str
    address: str
    distance: str
    maps_link: str
    message: str                # "Aapka mandap mil gaya!"

class TimelinePhase(BaseModel):
    phase: int
    name: str
    date: str
    description: str

class TimelineResponse(BaseModel):
    current_phase: str
    phases: list[TimelinePhase]
    next_deadline: str
    days_remaining: int
