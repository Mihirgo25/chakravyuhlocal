def main():
    from services.bramhastra.client import ClickHouse
    from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
    from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
    
    click = ClickHouse()
    
    click.execute("drop database brahmastra")
    
    click.execute("create database brahmastra")
    
    from database.create_clicks import Clicks
    
    Clicks(models = [AirFreightRateStatistic,FclFreightRateStatistic],ignore_oltp = True).create()

if __name__ == "__main__":
    main()