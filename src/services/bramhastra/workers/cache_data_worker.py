from services.bramhastra.helpers.fcl_freight_filter_helper import (
    get_direct_indirect_filters,
)
from services.bramhastra.constants import (
    DEFAULT_START_DATE,
    ALL_TIME_ACCURACY_JSON_FILE_PATH,
)
from datetime import date
from services.bramhastra.interactions.get_fcl_freight_rate_charts import (
    get_accuracy,
)
import json
from services.rate_sheet.interactions.upload_file import upload_media_file
from services.bramhastra.enums import DTString, RedisKeys
from database.db_session import rd


class Common:
    def __init__(self) -> None:
        pass

    def prepare_jsonfile(self, data, path) -> str:
        json_object = json.dumps(data, indent=4)
        with open(path, "wb") as outfile:
            outfile.write(json_object.encode("utf-8"))


class FclCacheData(Common):
    def __init__(self) -> None:
        pass

    def set_all_time_accuracy_chart(self):
        filters = dict(
            start_date=DEFAULT_START_DATE,
            end_date=date.today().isoformat(),
        )

        where = get_direct_indirect_filters(filters)

        accuracy = get_accuracy(filters, where)

        self.prepare_jsonfile(accuracy, ALL_TIME_ACCURACY_JSON_FILE_PATH)

        url = upload_media_file(ALL_TIME_ACCURACY_JSON_FILE_PATH)

        rd.set(RedisKeys.fcl_freight_rate_all_time_accuracy_chart.value, url)
