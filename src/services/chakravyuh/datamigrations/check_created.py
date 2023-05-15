import json
from configs.definitions import ROOT_DIR
import os
from configs.global_constants import CONTAINER_SIZES, CONTAINER_TYPES
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation

def check_missing_lanes():

    path = os.path.join(ROOT_DIR, '..', '.data', 'trade_lanes.json')
    f = open(path)
    trades = json.load(f)

    print('lk')

    combinations = []
    for cs in CONTAINER_SIZES:
        for ct in CONTAINER_TYPES:
            for trade in  trades:
                for trade1 in trades:
                    combinations.append({
                        'container_type': ct,
                        'container_size': cs,
                        'origin_location_id': trade['id'],
                        'destination_location_id': trade1['id'],
                        'origin': trade['name'],
                        'destination': trade1['name']
                    })
    missing = []
    c = 0
    m = 0
    for combination in combinations:
        print('kll')
        tf = FclFreightRateEstimation.select(FclFreightRateEstimation.id).where(
            FclFreightRateEstimation.origin_location_id == combination['origin_location_id'],
            FclFreightRateEstimation.destination_location_id == combination['destination_location_id'],
            FclFreightRateEstimation.container_size == combination['container_size'],
            FclFreightRateEstimation.container_type == combination['container_type'],
            FclFreightRateEstimation.origin_location_type == 'trade',
            FclFreightRateEstimation.destination_location_type == 'trade'
        )
        c = c + 1
        print(c, 'Print')
        if tf.count() == 0:
            print(m)
            missing.append(combination)
    
    print(len(missing))