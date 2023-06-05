from pydantic import BaseModel

class CreateFreightLookRatesParams(BaseModel):
  rates: list = [],
  destination: str = None