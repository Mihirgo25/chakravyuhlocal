from pydantic import BaseModel
from datetime import datetime
from pydantic import validator

# some classes have been ignored while adding to apis to reduce latency increased due to increased validations


def check_percentages(v):
    assert v < 100 and v > 0


class AccuracyValues(BaseModel):
    x: datetime
    y: float


class RateAccuracyChart(BaseModel):
    id: str
    data: list[AccuracyValues]


class RateDeviationChart(BaseModel):
    range: int
    count: int


class FclFreightRateCharts(BaseModel):
    accuracy: list[RateAccuracyChart]
    deviation: list[RateDeviationChart]
    rate_count_with_deviation_more_than_30: float
    spot_search_to_checkout_count: int


class FclFreightRateBooking(BaseModel):
    count: int
    confirmed_booking: int
    in_progress_booking: int
    completed_booking: int


class FclFreightRateDistribution(BaseModel):
    total_rates: int
    supply_rates: FclFreightRateBooking
    extended_rates: FclFreightRateBooking
    predicted_rates: FclFreightRateBooking


class RateDrillDownCount(BaseModel):
    from_search_to_checkout_drop_off: float

    @validator("from_search_to_checkout_drop_off")
    def validate_from_search_to_checkout_drop_off(cls, v):
        check_percentages(v)
        return v


class FclFreightRates(BaseModel):
    counts_with_deviation_more_than_x: int


class LifeCycle(BaseModel):
    action_type: str
    rates_count: int
    drop: float


class FclFreightRateLifeCycleResponse(BaseModel):
    searches: int
    cards: list[LifeCycle]


class DefaultList(BaseModel):
    list: list[dict]
    page: int
    page_limit: int
    total_pages: int
    total_count: int


class World(BaseModel):
    country_id: str
    rates_count: int
    country_name: str


class FclFreightRateWorldResponse(BaseModel):
    statistics: list[World]
    total_rates: int
    
class PortPair(BaseModel):
    origin_id: str
    destination_id: str
    rate_count: int
    
class PortPairRateCount(BaseModel):
    port_pair_rate_count: list[PortPair]
