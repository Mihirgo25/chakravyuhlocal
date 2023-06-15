from pydantic import BaseModel

class CreateFreightLookRatesParams(BaseModel):
  rates: list = [],
  destination: str = None

class CreateWebCargoRatesParams(BaseModel):
  rates: list = [],
  destination: str = None

class CreateNewMaxRatesParams(BaseModel):
  rates: list = [],
  destination: str = None