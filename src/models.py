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

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    alt_baro: float | None = None
    model_config = ConfigDict(extra="allow") 