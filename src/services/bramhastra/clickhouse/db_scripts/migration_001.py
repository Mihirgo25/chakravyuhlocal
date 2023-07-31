from services.bramhastra.clickhouse.client import ClickHouse

def main(client = ClickHouse().client):
    client.command("")

if __name__ == "__main__":
    main()