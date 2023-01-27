from pydantic import BaseModel as pydantic_base_model

class slab(pydantic_base_model):
  lower_limit: float
  upper_limit: float
  price: float
  currency: str