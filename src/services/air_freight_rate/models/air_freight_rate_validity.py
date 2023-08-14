from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from micro_services.client import maps
from services.air_freight_rate.air_freight_rate_params import WeightSlab
from pydantic import BaseModel
from uuid import UUID
from pydantic import BaseModel

class AirFreightRateValidity(BaseModel):
    validity_start: datetime.date
    validity_end: datetime.date
    min_price: float
    id: UUID
    currency: str
    status: bool = True
    likes_count: int = None
    dislikes_count: int = None
    weight_slabs: list[WeightSlab] = []
    density_category: str = 'general'
    initial_volume: float = None
    available_volume: float = None
    initial_gross_weight: float = None
    available_gross_weight: float = None
    min_density_weight: float = None
    max_density_weight: float = None
    flight_uuid: str = None
    external_rate_id: str = None

    # class Config:
    #     orm_mode = True
    #     exclude = ('validity_start', 'validity_end')

    def validations(self):
        if self.initial_volume and self.initial_volume < 0:
            raise HTTPException(status_code=400,detail = 'Initial Volume Should Be Positive')

        if self.available_volume and self.available_volume < 0:
            raise HTTPException(status_code=400,detail = 'Available Volume Should Be Positive')
        
        if self.initial_gross_weight and self.initial_gross_weight < 0:
            raise HTTPException(status_code=400,detail = 'Initial Gross Weight Be Positive')
        
        if self.available_gross_weight and self.available_gross_weight < 0:
            raise HTTPException(status_code=400,detail = 'Available Gross Weight Be Positive')
        
        if self.min_density_weight and self.min_density_weight < 0:
            raise HTTPException(status_code=400,detail = 'Minimum Density Weight Be Positive')
        
        if self.max_density_weight and self.max_density_weight < 0:
            raise HTTPException(status_code=400,detail = 'Maximum Density Weight Be Positive')
        
        self.validate_weight_slabs()
        return True
    
    def validate_weight_slabs(self):
        now = datetime.datetime.now()
        beginning_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not self.status and self.validity_end < beginning_of_day:
            return
        
        lower_limits = []
        upper_limits = []
        check = False
        self.weight_slabs = sorted(self.weight_slabs, key=lambda x: x.lower_limit)

        for slab in self.weight_slabs:
            if float(slab.upper_limit) <= float(slab.lower_limit):
                check = True
            lower_limits.append(slab.lower_limit)
            upper_limits.append(slab.upper_limit)
        if check:
            raise HTTPException(status_code = 400,detail = 'Invalid Weight Slabs')
        
        for i in range(len(upper_limits) - 1):
            if upper_limits[i] >= lower_limits[i + 1]:
                raise HTTPException(status_code = 400,detail = 'Weight Slabs OverLapping')