from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)

data = {
    "100": [
        {"level": 1, "price": 270},
        {"level": 2, "price": 310},
        {"level": 3, "price": 350},
    ],
    "700": [
        {"level": 1, "price": 210},
        {"level": 2, "price": 250},
        {"level": 3, "price": 290},
    ],
    "1300": [
        {"level": 1, "price": 195},
        {"level": 2, "price": 235},
        {"level": 3, "price": 275},
    ],
    "2000": [
        {"level": 1, "price": 180},
        {"level": 2, "price": 220},
        {"level": 3, "price": 260},
    ],
}


def insert_vietnam():
    for i, d in data.items():
        print(i)
        print(d)
        for itr in d:
            HaulageFreightRateRuleSet.create(
                distance=float(i),
                train_load_type='Wagon Load',
                commodity_class_type=itr["level"],
                base_price=float(itr["price"]),
                country_code="VN",
                currency="VND",
            )
            # except:
            #     continue
    return
