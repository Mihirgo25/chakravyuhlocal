from micro_services.client import maps
from fastapi import HTTPException
from services.ftl_freight_rate.models.fuel_data import FuelData
from database.db_session import db


def create_fuel_data(request):
    with db.atomic() as transaction:
        try:
            response = execute_fuel_data_transaction(request)
            return response
        except:
            transaction.rollback()
            raise


def execute_fuel_data_transaction(request):
    fuel_data_search_params = get_search_params(request)
    fuel_data_id = find_fuel_data(fuel_data_search_params)

    if fuel_data_id:
        fuel_data_id = assign_attribute(fuel_data_id, request)
    else:
        fuel_data_id = create_new_fuel_data(request)

    return {"id": str(fuel_data_id)}


def get_search_params(request):
    search_params = {}
    for search_key in ["location_id", "location_type", "fuel_type"]:
        search_params[search_key] = request[search_key]
    return search_params


def find_fuel_data(fuel_data_search_params):
    fuel_data_id = (
        FuelData.select(FuelData.id)
        .where(
            FuelData.location_id == str(fuel_data_search_params["location_id"]),
            FuelData.location_type == str(fuel_data_search_params["location_type"]),
            FuelData.fuel_type == str(fuel_data_search_params["fuel_type"]),
        )
        .first()
    )
    return fuel_data_id


def assign_attribute(fuel_data_id, request):
    update_params = {}
    for key in ["fuel_price", "fuel_unit", "currency"]:
        update_params[key] = request[key]
    FuelData.update(update_params).where(FuelData.id == str(fuel_data_id)).execute()
    return fuel_data_id


def create_new_fuel_data(request):
    fuel_data = FuelData.create(
        location_id=request["location_id"],
        location_type=request["location_type"],
        fuel_type=request["fuel_type"],
        currency=request["currency"],
        fuel_unit=request["fuel_unit"],
        fuel_price=float(request["fuel_price"]),
    )
    return fuel_data.id
