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
    id: str
    date: datetime
    value: float


class FclFreightRateCharts(BaseModel):
    deviation: list[RateDeviationChart]
    rate_count_with_deviation_more_than_30: int
    accuracy: list[RateAccuracyChart]
    drilldown: float


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


class DrillDown(BaseModel):
    key: str
    count: int
    drop_off: float

    @validator("drop_off")
    def validate_drop_off(cls, v):
        check_percentages(v)
        return v


class FclFreightRateDrillDownResponse(BaseModel):
    spot_searches_count: int
    array_1: list[DrillDown]
    array_2: list[DrillDown]
    array_3: list[DrillDown]


class MapDeviations(BaseModel):
    location_id: str
    value: float


class FclFreightMapViewResponse(BaseModel):
    origin_deviation: float = None
    destination_deviations: list[MapDeviations]
