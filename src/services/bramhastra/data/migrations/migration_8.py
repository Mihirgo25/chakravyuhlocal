from services.bramhastra.client import ClickHouse


def backup():
    client = ClickHouse()
    client.execute(
        """SELECT * FROM brahmastra.stale_fcl_freight_rate_statistics INTO OUTFILE 'fcl_freight_rate_statistics_1.csv' FORMAT CSVWithNames"""
    )
    client.execute(
        """SELECT * FROM brahmastra.stale_air_freight_rate_statistics INTO OUTFILE 'air_freight_rate_statistics_1.csv' FORMAT CSVWithNames"""
    )


if __name__ == "__main__":
    backup()
