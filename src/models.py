import pydantic
from pydantic import ConfigDict, model_validator, Field

class AircraftModel(pydantic.BaseModel):
    acft_ID: str = Field(pattern=r"^[0-9a-f]{6}$")
    model_config = ConfigDict(extra="allow") 

class PositionModel(pydantic.BaseModel):
    @model_validator(mode="before")
    @classmethod
    def ground_alt(cls, data):  
        if data.get("alt_baro") == "ground" :
            data["alt_baro"] = 0
            data["on_ground"] = True
        else:
            data["on_ground"] = False
        return data
    
    @model_validator(mode="before")
    @classmethod
    def resolve_position(cls, data):
        if data.get("lat") is not None and data.get("lon") is not None:
            data["position_source"] = "exact"
            data.pop("rr_lat", None)
            data.pop("rr_lon", None)
            data.pop("lastPosition", None)
        elif data.get("rr_lat") is not None and data.get("rr_lon") is not None:
            data["lat"] = data["rr_lat"]
            data["lon"] = data["rr_lon"]
            data.pop("rr_lat", None)
            data.pop("rr_lon", None)
            data.pop("lastPosition", None)
            data["position_source"] = "rounded"
        elif "lastPosition" in data and data["lastPosition"].get("lat") is not None:
            data["lat"] = data["lastPosition"]["lat"]
            data["lon"] = data["lastPosition"]["lon"]
            data.pop("rr_lat", None)
            data.pop("rr_lon", None)
            data.pop("lastPosition", None)
            data["position_source"] = "stale"
        else:
            raise ValueError("no position data available")
        return data
    
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    alt_baro: float | None = None
    on_ground: bool
    position_source: Literal["exact", "rounded", "stale"]
    model_config = ConfigDict(extra="allow") 