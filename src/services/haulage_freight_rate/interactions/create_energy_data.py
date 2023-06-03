from fastapi import HTTPException
from services.haulage_freight_rate.models.energy_data import EnergyData
from database.db_session import db


def create_energy_data(request):
    with db.atomic() as transaction:
        try:
            response = execute_energy_data_transaction(request)
            return response
        except:
            transaction.rollback()
            raise



def execute_energy_data_transaction(request):
    energy_data_search_params = get_search_params(request)
    energy_data_id = find_energy_data(energy_data_search_params)

    if energy_data_id:
        energy_data_id = assign_attribute(energy_data_id, request)
    else:
        energy_data_id = create_new_energy_data(request)

    return {"id": str(energy_data_id)}

def get_search_params(request):
    search_params = {}
    for search_key in ["country_code", "currency", "fuel_price"]:
        search_params[search_key] = request[search_key]
    return search_params

def find_energy_data(fuel_data_search_params):
    fuel_data_id = (
        EnergyData.select(EnergyData.id)
        .where(
            EnergyData.country_code == str(fuel_data_search_params["country_code"]),
            EnergyData.currency == str(fuel_data_search_params["currency"]),
            EnergyData.fuel_price == str(fuel_data_search_params["fuel_price"]),
        )
        .first()
    )
    return fuel_data_id


def assign_attribute(fuel_data_id, request):
    update_params = {}
    for key in ["country_code", "currency", "fuel_price"]:
        update_params[key] = request[key]
    EnergyData.update(update_params).where(EnergyData.id == str(fuel_data_id)).execute()
    return fuel_data_id



def create_new_energy_data(request):
    fuel_data = EnergyData.create(
        fuel_type=request["fuel_type"],
        currency=request["currency"],
        fuel_price=request["fuel_price"],
        country_code=float(request["country_code"]),
        fuel_unit=request["fuel_unit"],
    )
    return fuel_data.id