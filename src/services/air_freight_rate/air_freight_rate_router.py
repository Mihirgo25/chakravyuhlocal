from fastapi import APIRouter, Query, Depends

air_freight_router = APIRouter()


@air_freight_router.post("/create_air_freight_rate")
def create_air_freight_rate():
    return
