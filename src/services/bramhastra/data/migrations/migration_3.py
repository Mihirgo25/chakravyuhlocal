import json
import urllib
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from joblib import delayed, Parallel, cpu_count

class ParallelJobs:
    def __init__(self):
        self.count_of_cpus = cpu_count()
        self.verbose = 100

    def parallel_function(self, parallel_list, function_call):
        parallel_pool = Parallel(
            n_jobs=self.count_of_cpus, prefer="threads", verbose=self.verbose
        )
        functions = [delayed(function_call)(each) for each in parallel_list]
        res = parallel_pool(functions)
        return res

def main():
    REGION_MAPPING_URL = "https://cogoport-production.sgp1.digitaloceanspaces.com/d1046f77b58f68f14ab034bafd7d243d/region_to_port.json"

    REGION_MAPPING = {}
    with urllib.request.urlopen(REGION_MAPPING_URL) as url:
        REGION_MAPPING = json.loads(url.read().decode())
        
    pj = ParallelJobs()
    
    pj.parallel_function(REGION_MAPPING,adjust)


def adjust(mapping):
    port_id = mapping["id"]
    region_id = mapping["region_id"]

    if port_id and region_id:
        origin_count = (
            FclFreightRateStatistic.select(FclFreightRateStatistic.id)
            .where(FclFreightRateStatistic.origin_port_id == port_id)
            .count()
        )

        if origin_count:
            FclFreightRateStatistic.update(origin_region_id=region_id).where(
                FclFreightRateStatistic.origin_port_id == port_id
            )

        destination_count = (
            FclFreightRateStatistic.select(FclFreightRateStatistic.id)
            .where(FclFreightRateStatistic.destination_port_id == port_id)
            .count()
        )

        if destination_count:
            FclFreightRateStatistic.update(destination_region_id=region_id).where(
                FclFreightRateStatistic.destination_port_id == port_id
            )

if __name__ == "__main__":
    main()