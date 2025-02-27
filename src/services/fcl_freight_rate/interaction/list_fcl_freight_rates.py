from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_properties import (
    FclFreightRateProperties,
)
from configs.global_constants import SEARCH_START_DATE_OFFSET
from datetime import datetime, timedelta
from libs.get_filters import get_filters
from libs.apply_eligible_lsp_filters import apply_eligible_lsp_filters
from libs.get_applicable_filters import get_applicable_filters
import json
import math
from configs.fcl_freight_rate_constants import RATE_TYPES
from libs.json_encoder import json_encoder
from peewee import SQL

NOT_REQUIRED_FIELDS = [
    "destination_local_line_items_info_messages",
    "origin_local_line_items_info_messages",
    "origin_local_line_items_error_messages",
    "destination_local_line_items_error_messages",
    "destination_location_ids",
    "origin_location_ids",
    "omp_dmp_sl_sp",
    "init_key",
]

possible_direct_filters = [
    "id",
    "origin_port_id",
    "origin_country_id",
    "origin_trade_id",
    "origin_continent_id",
    "destination_port_id",
    "destination_country_id",
    "destination_trade_id",
    "destination_continent_id",
    "shipping_line_id",
    "service_provider_id",
    "importer_exporter_id",
    "container_size",
    "container_type",
    "commodity",
    "is_best_price",
    "rate_not_available_entry",
    "origin_main_port_id",
    "destination_main_port_id",
    "cogo_entity_id",
    "procured_by_id",
    "rate_type",
    "mode",
]
possible_indirect_filters = [
    "is_origin_local_missing",
    "is_destination_local_missing",
    "is_weight_limit_missing",
    "is_origin_detention_missing",
    "is_origin_plugin_missing",
    "is_destination_detention_missing",
    "is_destination_demurrage_missing",
    "is_destination_plugin_missing",
    "is_rate_about_to_expire",
    "is_rate_available",
    "is_rate_not_available",
    "origin_location_ids",
    "destination_location_ids",
    "importer_exporter_present",
    "last_rate_available_date_greater_than",
    "last_rate_available_date_less_than",
    "validity_start_greater_than",
    "validity_end_less_than",
    "partner_id",
    "importer_exporter_relevant_rate",
    "exclude_shipping_line_id",
    "exclude_service_provider_types",
    "exclude_rate_types",
    "service_provider_type",
    "updated_at_greater_than",
    "updated_at_less_than",
    "updated_at_greater_than_time",
    "updated_at_less_than_time",
    "get_cogo_assured_checkout_rates",
    "exclude_service_provider_id",
    "exclude_mode",
    "exclude_tag",
]

EXCLUDED_PROPERTIES = ["id", "created_at", "updated_at"]


def list_fcl_freight_rates(
    filters={},
    page_limit=10,
    page=1,
    sort_by=None,
    sort_type="desc",
    return_query=False,
    expired_rates_required=False,
    return_count=False,
    is_line_items_required=False,
    includes={},
    pagination_data_required=False,
):
    query = get_query(sort_by, sort_type, includes)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        if not filters.get("id") and not filters.get("rate_type"):
            filters["rate_type"] = [
                rate for rate in RATE_TYPES if rate != "cogo_assured"
            ]
        elif filters.get("rate_type") == "all":
            filters.pop("rate_type")

        direct_filters, indirect_filters = get_applicable_filters(
            filters, possible_direct_filters, possible_indirect_filters
        )

        query = get_filters(direct_filters, query, FclFreightRate)
        query = apply_indirect_filters(query, indirect_filters)

    if not filters or not "service_provider_id" in filters:
        query = apply_eligible_lsp_filters(query, FclFreightRate, "fcl_freight")

    if return_count:
        return {"total_count": query.count()}

    pagination_data = (
        get_pagination_data(query, page, page_limit) if pagination_data_required else {}
    )

    if page_limit:
        query = query.paginate(page, page_limit)

    if return_query:
        return {"list": query}

    data = get_data(query, expired_rates_required, is_line_items_required)

    return {"list": data} | pagination_data


def get_query(sort_by, sort_type, includes):
    if includes and not isinstance(includes, dict):
        includes = json.loads(includes)

    fcl_all_fields = list(FclFreightRate._meta.fields.keys())
    required_fcl_fields = (
        [a for a in includes.keys() if a in fcl_all_fields]
        if includes
        else [c for c in fcl_all_fields if c not in NOT_REQUIRED_FIELDS]
    )
    fcl_fields = [getattr(FclFreightRate, key) for key in required_fcl_fields]

    properties_all_fields = list(FclFreightRateProperties._meta.fields.keys())
    required_properties_fields = (
        list(
            c
            for c in includes.keys()
            if c in properties_all_fields and c not in EXCLUDED_PROPERTIES
        )
        if includes
        else []
    )
    properties_fields = [
        getattr(FclFreightRateProperties, key) for key in required_properties_fields
    ]

    fields = fcl_fields + properties_fields

    query = FclFreightRate.select(*fields)

    if sort_by:
        query = query.order_by(
            eval("FclFreightRate.{}.{}()".format(sort_by, sort_type))
        )

    return query


def get_data(query, expired_rates_required, is_line_items_required):
    data = []

    raw_data = json_encoder(list(query.dicts()))

    for result in raw_data:
        result["is_weight_limit_missing"] = False

        if not result.get("weight_limit") or "free_limit" not in result["weight_limit"]:
            result["is_weight_limit_missing"] = True

        validities = []

        if result.get("validities"):
            for validity_object in result["validities"]:
                if (
                    datetime.strptime(validity_object["validity_end"], "%Y-%m-%d")
                    <= datetime.now()
                ) and (not expired_rates_required):
                    continue

                platform_price = validity_object.get("platform_price") or -1

                validity = {
                    "id": validity_object["id"],
                    "validity_start": validity_object["validity_start"],
                    "validity_end": validity_object["validity_end"],
                    "price": validity_object["price"],
                    "platform_price": platform_price,
                    "market_price": validity_object.get("market_price")
                    or validity_object["price"],
                    "currency": validity_object["currency"],
                    "is_rate_about_to_expire": (
                        datetime.strptime(validity_object["validity_end"], "%Y-%m-%d")
                        >= datetime.now()
                    )
                    & (
                        datetime.strptime(validity_object["validity_end"], "%Y-%m-%d")
                        < (datetime.now() + timedelta(days=SEARCH_START_DATE_OFFSET))
                    ),
                    "is_best_price": (validity_object["price"] == platform_price),
                    "schedule_type": validity_object["schedule_type"],
                    "payment_type": validity_object["payment_term"],
                    "schedule_id": validity_object.get("schedule_id"),
                    "is_rate_expired": datetime.strptime(
                        validity_object["validity_end"], "%Y-%m-%d"
                    )
                    < datetime.now(),
                }
                if is_line_items_required:
                    validity["line_items"] = validity_object["line_items"]

                validities.append(validity)
                result["validities"] = validities

                result["is_rate_not_available"] = validities.count == 0
        if validities:
            data.append(result)
    return data


def apply_indirect_filters(query, filters):
    for key in filters:
        apply_filter_function = f"apply_{key}_filter"
        query = eval(f"{apply_filter_function}(query, filters)")
    return query


def apply_importer_exporter_relevant_rate_filter(query, filters):
    importer_exporter_id = filters["importer_exporter_relevant_rate"]
    query = query.where(
        (FclFreightRate.importer_exporter_id == importer_exporter_id)
        | (FclFreightRate.importer_exporter_id.is_null(True))
    )
    return query


def apply_get_cogo_assured_checkout_rates_filter(query, filters):
    if filters.get("get_cogo_assured_checkout_rates"):
        query = query.join(
            FclFreightRateProperties,
            on=(FclFreightRate.id == FclFreightRateProperties.rate_id),
        ).where(
            FclFreightRateProperties.available_inventory
            > FclFreightRateProperties.used_inventory
        )
    return query


def apply_partner_id_filter(query, filters):
    cogo_entity_id = filters["partner_id"]
    if cogo_entity_id:
        query = query.where(FclFreightRate.cogo_entity_id.in_([cogo_entity_id]))
    else:
        query = query.where(FclFreightRate.cogo_entity_id == None)
    return query


def apply_is_origin_local_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_origin_local_line_items_error_messages_present"] == True
        or filters["is_origin_local_line_items_error_messages_present"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(
            FclFreightRate.is_origin_local_line_items_error_messages_present
        )
    else:
        query = query.where(
            (
                FclFreightRate.is_origin_local_line_items_error_messages_present
                == None
                | ~FclFreightRate.is_origin_local_line_items_error_messages_present
            )
        )
    return query


def apply_is_destination_local_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_destination_local_line_items_error_messages_present"] == True
        or filters["is_destination_local_line_items_error_messages_present"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(
            FclFreightRate.is_destination_local_line_items_error_messages_present
        )
    else:
        query = query.where(
            (
                FclFreightRate.is_destination_local_line_items_error_messages_present
                == None
                | ~FclFreightRate.is_destination_local_line_items_error_messages_present
            )
        )
    return query


def apply_is_weight_limit_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_weight_limit_slabs_missing"] == True
        or filters["is_weight_limit_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_weight_limit_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_weight_limit_slabs_missing
                == None | ~FclFreightRate.is_weight_limit_slabs_missing
            )
        )

    return query


def apply_is_origin_detention_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_origin_detention_slabs_missing"] == True
        or filters["is_origin_detention_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_origin_detention_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_origin_detention_slabs_missing
                == None | ~FclFreightRate.is_origin_detention_slabs_missing
            )
        )
    return query


def apply_is_origin_plugin_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_origin_plugin_slabs_missing"] == True
        or filters["is_origin_plugin_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_origin_plugin_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_origin_plugin_slabs_missing
                == None | ~FclFreightRate.is_origin_plugin_slabs_missing
            )
        )

    return query


def apply_is_destination_detention_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_destination_detention_slabs_missing"] == True
        or filters["is_destination_detention_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_destination_detention_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_destination_detention_slabs_missing
                == None | ~FclFreightRate.is_destination_detention_slabs_missing
            )
        )

    return query


def apply_is_destination_demurrage_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_destination_demurrage_slabs_missing"] == True
        or filters["is_destination_demurrage_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_destination_demurrage_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_destination_demurrage_slabs_missing
                == None | ~FclFreightRate.is_destination_demurrage_slabs_missing
            )
        )

    return query


def apply_is_destination_plugin_missing_filter(query, filters):
    is_messages = False
    if (
        filters["is_destination_plugin_slabs_missing"] == True
        or filters["is_destination_plugin_slabs_missing"] == "True"
    ):
        is_messages = True
    if is_messages:
        query = query.where(FclFreightRate.is_destination_plugin_slabs_missing)
    else:
        query = query.where(
            (
                FclFreightRate.is_destination_plugin_slabs_missing
                == None | ~FclFreightRate.is_destination_plugin_slabs_missing
            )
        )

    return query


def apply_is_rate_about_to_expire_filter(query, filters):
    query = (
        query.where(FclFreightRate.last_rate_available_date != None)
        .where(FclFreightRate.last_rate_available_date >= datetime.now().date())
        .where(
            FclFreightRate.last_rate_available_date
            < (datetime.now().date() + timedelta(days=SEARCH_START_DATE_OFFSET))
        )
    )
    return query


def apply_is_rate_not_available_filter(query, filters):
    query = query.where(
        (FclFreightRate.last_rate_available_date == None)
        | (FclFreightRate.last_rate_available_date < datetime.now().date())
    )
    return query


def apply_is_rate_available_filter(query, filters):
    query = query.where(
        FclFreightRate.last_rate_available_date >= datetime.now().date()
    )
    return query


def apply_origin_location_ids_filter(query, filters):
    locations_ids = filters["origin_location_ids"]
    query = query.where(FclFreightRate.origin_location_ids.contains(locations_ids))
    return query


def apply_destination_location_ids_filter(query, filters):
    locations_ids = filters["destination_location_ids"]
    query = query.where(FclFreightRate.destination_location_ids.contains(locations_ids))
    return query


def apply_importer_exporter_present_filter(query, filters):
    if filters["importer_exporter_present"]:
        return query.where(FclFreightRate.importer_exporter_id != None)

    query = query.where(FclFreightRate.importer_exporter_id == None)
    return query


def apply_last_rate_available_date_greater_than_filter(query, filters):
    query = query.where(
        FclFreightRate.last_rate_available_date.cast("date")
        >= datetime.fromisoformat(
            filters["last_rate_available_date_greater_than"]
        ).date()
    )
    return query


def apply_last_rate_available_date_less_than_filter(query, filters):
    query = query.where(
        FclFreightRate.last_rate_available_date.cast("date")
        <= datetime.fromisoformat(filters["last_rate_available_date_less_than"]).date()
    )
    return query


def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(
        FclFreightRate.last_rate_available_date.cast("date")
        >= datetime.fromisoformat(filters["validity_start_greater_than"]).date()
    )
    return query


def apply_validity_end_less_than_filter(query, filters):
    query = query.where(
        FclFreightRate.last_rate_available_date.cast("date")
        <= datetime.fromisoformat(filters["validity_end_less_than"]).date()
    )
    return query


def apply_exclude_tag_filter(query, filters):
    tag = filters.get("exclude_tag")
    query = query.where(
        SQL(
            f"""
            NOT EXISTS (
                SELECT 1
                FROM jsonb_each_text(tags) AS kv
                WHERE kv.value = '{tag}'
            )
            """
        )
    )
    return query


def apply_updated_at_greater_than_filter(query, filters):
    query = query.where(
        FclFreightRate.updated_at.cast("date")
        >= datetime.fromisoformat(filters["updated_at_greater_than"]).date()
    )
    return query


def apply_updated_at_less_than_filter(query, filters):
    query = query.where(
        FclFreightRate.updated_at.cast("date")
        <= datetime.fromisoformat(filters["updated_at_less_than"]).date()
    )
    return query


def apply_updated_at_greater_than_time_filter(query, filters):
    query = query.where(
        FclFreightRate.updated_at
        >= datetime.fromisoformat(filters["updated_at_greater_than_time"])
    )
    return query


def apply_updated_at_less_than_time_filter(query, filters):
    query = query.where(
        FclFreightRate.updated_at
        <= datetime.fromisoformat(filters["updated_at_less_than_time"])
    )
    return query


def apply_procured_by_id_filter(query, filters):
    query = query.where(FclFreightRate.procured_by_id == filters["procured_by_id"])
    return query


def apply_exclude_shipping_line_id_filter(query, filters):
    shipping_line_ids = filters["exclude_shipping_line_id"]
    if not isinstance(shipping_line_ids, list):
        shipping_line_ids = [shipping_line_ids]
    query = query.where(~FclFreightRate.shipping_line_id << shipping_line_ids)
    return query


def apply_exclude_service_provider_id_filter(query, filters):
    exclude_service_provider_ids = filters["exclude_service_provider_id"]
    if not isinstance(exclude_service_provider_ids, list):
        exclude_service_provider_ids = [exclude_service_provider_ids]
    query = query.where(
        FclFreightRate.service_provider_id.not_in(exclude_service_provider_ids)
    )
    return query


def apply_service_provider_type_filter(query, filters):
    category_types = filters["service_provider_type"]
    if not isinstance(category_types, list):
        category_types = [category_types]
    query = query.where(
        FclFreightRate.service_provider["category_types"].contains_any(category_types)
    )
    return query


def apply_exclude_service_provider_types_filter(query, filters):
    query = query.where(
        ~FclFreightRate.service_provider["category_types"].contains_any(
            filters["exclude_service_provider_types"]
        )
    )
    return query


def apply_exclude_rate_types_filter(query, filters):
    query = query.where(~FclFreightRate.rate_type << filters["exclude_rate_types"])
    return query


def apply_exclude_mode_filter(query, filters):
    exclude_modes = filters["exclude_mode"]
    if not isinstance(exclude_modes, list):
        exclude_modes = [exclude_modes]
    query = query.where(FclFreightRate.mode.not_in(exclude_modes))
    return query


def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    pagination_data = {
        "page": page,
        "total": math.ceil(total_count / page_limit),
        "total_count": total_count,
        "page_limit": page_limit,
    }

    return pagination_data
