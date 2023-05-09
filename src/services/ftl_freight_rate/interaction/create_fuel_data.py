from micro_services.client import maps
from fastapi import HTTPException
from services.ftl_freight_rate.models.fuel_data import FuelData
from database.db_session import db


def create_fuel_data(request):
    with db.atomic() as transaction:
        try:
            response = execute_fuel_data_transaction(
               request
            )
            return response
        except:
            transaction.rollback()
            raise


def execute_fuel_data_transaction(request):
    fuel_data_search_params = get_search_params(request)
    fuel_data = find_fuel_data(fuel_data_search_params)
    if fuel_data:
        fuel_data = assign_attribute(fuel_data,request)
    else:
        fuel_data = create_new_fuel_data(request)

    fuel_data.save()


    return {id: fuel_data.id}


def get_search_params(request):
    search_params = {}
    for search_key in ["location_id", "location_type", "fuel_type"]:
        search_params[search_key] = request[search_key]
    return search_params


def find_fuel_data(fuel_data_search_params):
    fuel_data_object = (
        FuelData.select()
        .where(
            FuelData.location_id == str(fuel_data_search_params["location_id"]),
            FuelData.location_type == str(fuel_data_search_params["location_type"]),
            FuelData.fuel_type   == str(fuel_data_search_params["fuel_type"]),
        )
        .first()
    )
    print(fuel_data_object,"asd")
    return fuel_data_object  


def assign_attribute(fuel_data_object, request):
    update_params = {}
    for key in ['fuel_price','fuel_unit','currency']:
        update_params[key] = request[key]
    fuel_data_id = fuel_data_object.id
    fuel_data_object = FuelData.update(update_params).where(FuelData.id == str(fuel_data_id)).save()
    print(fuel_data_object,"ASDAS")
    return fuel_data_object


def create_new_fuel_data(request):
    print("ADASDS")
    return FuelData.create(
            location_id = request['location_id'],
            location_type = request['location_type'],
            fuel_type = request['fuel_type'],
            currency = request['currency'],
            fuel_unit = request['fuel_unit'],
            fuel_price = request['fuel_price']
        )
