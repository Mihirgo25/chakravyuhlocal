from services.bramhastra.clickhouse.connect import get_clickhouse_client

def main(client = get_clickhouse_client()):
    client.command("")

if __name__ == "__main__":
    main()