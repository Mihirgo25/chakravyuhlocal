from services.ftl_freight_rate.models.truck import Truck
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from operator import attrgetter

SELECTED_TRUCK_FIELDS = [
    "id",
    "truck_company",
    "truck_name",
    "mileage",
    "mileage_unit",
    "capacity",
    "capacity_unit",
    "vehicle_weight",
    "vehicle_weight_unit",
    "fuel_type",
    "no_of_wheels",
    "country_id",
    "truck_type",
    "body_type",
    "status",
]


def get_truck_detail(request):
    truck_search_params = get_search_params(request)
    if truck_search_params:
        truck_search_params = get_search_params(truck_search_params)
        truck_detail = find_truck_detail(truck_search_params)
        if truck_detail:
            return {"truck_detail": truck_detail}

    return {"truck_detail": "No truck found"}


def get_search_params(request):
    if request.get("id"):
        return {"id": request.get("id"), "status": "active"}
    elif request.get("truck_name"):
        return {"truck_name": request.get("truck_name"), "status": "active"}
    return False


def find_truck_detail(truck_search_params):
    query = Truck.select()
    for key in truck_search_params:
        query = query.where(attrgetter(key)(Truck) == truck_search_params[key])

    truck_object = query.first()
    if not truck_object:
        return False
    truck_data_object = jsonable_encoder(model_to_dict(truck_object))
    truck_detail = {}
    for key in SELECTED_TRUCK_FIELDS:
        truck_detail[key] = truck_data_object[key]
    return truck_detail
