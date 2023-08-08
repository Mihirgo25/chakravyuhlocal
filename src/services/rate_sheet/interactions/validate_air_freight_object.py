import services.rate_sheet.interactions.validate_air_freight_object as validate_rate_sheet
from micro_services.client import *
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import (
    AirFreightRateSurcharge,
)


def validate_air_freight_object(module, object):
    response = {}
    response["valid"] = False
    try:
        rate_object = getattr(validate_rate_sheet, "get_{}_object".format(module))(object)
        if rate_object["error"].strip():
            response["error"] = rate_object["error"]
        else:
            response["valid"] = True
    except Exception as e:
        response['error'] = e
    return response


def get_freight_object(object):
    validation = {}
    rate_object = {}
    validation["error"] = ""
    res = object
    res["rate_not_available_entry"] = False
    rate_object = AirFreightRate(**res)
    rate_object.length = 300
    rate_object.breadth = 300
    rate_object.height = 300
    rate_object.price_type = object.get("price_type")

    try:
        rate_object.set_locations()
        rate_object.set_origin_location_ids()
        rate_object.set_destination_location_ids()
    except:
        validation["error"] += " Invalid location"
    
    if validation['error'].strip():
        return validation

    try:
        rate_object.validate_validity_object(
            object["validity_start"], object["validity_end"]
        )
    except HTTPException as e:
        validation["error"] += " " + str(e.detail)

    if validation['error'].strip():
        return validation

    try:
        validity_id = rate_object.set_validities(
            object.get("validity_start").date(),
            object.get("validity_end").date(),
            object.get("min_price"),
            object.get("currency"),
            object.get("weight_slabs"),
            False,
            None,
            object.get("density_category"),
            object.get("density_ratio"),
            object.get("initial_volume"),
            object.get("initial_gross_weight"),
            object.get("available_volume"),
            object.get("available_gross_weight"),
            object.get("rate_type"),
        )
        if object.get("mode") == "cargo_ai":
            rate_object.add_flight_and_external_uuid(
                validity_id, object.get("flight_uuid"), object.get("external_rate_id")
            )

        rate_object.set_last_rate_available_date()
    except HTTPException as e:
        validation["error"] += " " + str(e.detail)

    if validation['error'].strip():
        return validation

    try:
        rate_object.validate_before_save()
    except HTTPException as e:
        validation["error"] += " " + str(e.detail)
    
    if validation['error'].strip():
        return validation

    if not is_float(object.get("min_price")):
        validation["error"] += " min_price is invalid"
    
    if validation['error'].strip():
        return validation

    for weight_slab in object["weight_slabs"]:
        if not is_float(weight_slab.get("lower_limit")):
            validation["error"] += " lower_limit is invalid"
        else:
            weight_slab["lower_limit"] = float(weight_slab["lower_limit"])

        if not is_float(weight_slab.get("upper_limit")):
            validation["error"] += " upper_limit is invalid"
        else:
            weight_slab["upper_limit"] = float(weight_slab["upper_limit"])

        if not is_float(weight_slab.get("tariff_price")):
            validation["error"] += " tariff_price is invalid"
        else:
            weight_slab["tariff_price"] = float(weight_slab["tariff_price"])
    return validation


def get_local_object(object):
    validation = {}
    rate_object = {}
    validation["error"] = ""
    res = object
    res["rate_not_available_entry"] = False
    rate_object = AirFreightRateLocal(**res)
    try:
        rate_object.set_locations()
        rate_object.set_airline()
        rate_object.set_location_ids()
        rate_object.line_items = object.get("line_items")
    except:
        validation["error"] += " Invalid location"
    
    if validation['error'].strip():
        return validation

    try:
        rate_object.validate()
    except HTTPException as e:
        validation["error"] += " " + str(e.detail)

    return validation


def get_surcharge_object(object):
    validation = {}
    rate_object = {}
    validation["error"] = ""
    res = object
    res["rate_not_available_entry"] = False
    rate_object = AirFreightRateSurcharge(**res)
    try:
        rate_object.line_items = object.get("line_items")
        rate_object.set_locations()
        rate_object.set_destination_location_ids()
        rate_object.set_origin_location_ids()
        rate_object.set_locations()
    except:
        validation["error"] += " Invalid location"
    
    if validation['error'].strip():
        return validation
    
    try:
        rate_object.update_freight_objects()
        rate_object.update_line_item_messages()
        rate_object.validate()
    except HTTPException as e:
        validation["error"] += " " + str(e.detail)

    return validation


def is_float(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
