from services.bramhastra.helpers.filter_helper import (
    get_direct_indirect_filters,
)
from services.bramhastra.constants import DEFAULT_START_DATE,ALL_TIME_ACCURACY_JSON_FILE_PATH
from datetime import date
from services.bramhastra.interactions.get_fcl_freight_rate_charts import get_accuracy,format_charts
import json
from services.bramhastra.helpers.s3_upload import S3Upload
from services.bramhastra.enums import DTString, RedisKeys
from database.db_session import rd

class CacheData:
    async def __init__(self) -> None:
        await self.set_all_time_accuracy_chart

    async def set_all_time_accuracy_chart(self):
        filters = {'start_date': DEFAULT_START_DATE,'end_date': date.today().isoformat()}
        
        where = get_direct_indirect_filters(filters)
        
        accuracy = await get_accuracy(filters,where)
        
        response = format_charts(accuracy)
        
        self.prepare_jsonfile(response,ALL_TIME_ACCURACY_JSON_FILE_PATH)
        
        url = S3Upload(DTString.rate_monitoring.value,ALL_TIME_ACCURACY_JSON_FILE_PATH).get_url()
        
        rd.set(RedisKeys.fcl_freight_rate_all_time_accuracy_chart.value,url)
        
    def prepare_jsonfile(self,data,path) -> str:
        json_object = json.dumps(data, indent=4)
        with open(path, "w") as outfile:
            outfile.write(json_object)