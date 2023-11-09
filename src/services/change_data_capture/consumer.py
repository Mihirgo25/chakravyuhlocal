from kafka import KafkaConsumer
from json import loads
from configs.env import GROUP_ID, TOPIC_NAME, BOOTSTRAP_SERVER_1
from services.bramhastra.celery import brahmastra_v2_in_delay
import threading
from aiokafka import AIOKafkaConsumer
import asyncio

LOOP = asyncio.get_event_loop()

THRESHOLD = 1000


class AsyncConsumer:
    def __init__(self) -> None:
        self.consumer = AIOKafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=BOOTSTRAP_SERVER_1,
            group_id=GROUP_ID,
            loop=LOOP,
        )

    async def _start(self):
        await self.consumer.start()
        try:
            print("listening")
            async for msg in self.consumer:
                print("consumed: ", loads(msg.value.decode("utf-8")))
        except KeyboardInterrupt:
            pass
        finally:
            await self.consumer.stop()

    def start(self):
        asyncio.create_task(self._start())


class Consumer:
    def __init__(self) -> None:
        self.consumer = KafkaConsumer(
            TOPIC_NAME,
            value_deserializer=lambda x: loads(x.decode("utf-8")),
            bootstrap_servers=[BOOTSTRAP_SERVER_1],
            group_id=GROUP_ID,
        )

    def stop(self):
        self.consumer.close()

    def start(self):
        self.shutdown_event = threading.Event()
        self.thread = threading.Thread(target=self._start)
        self.thread.start()

    def stop(self):
        self.consumer.close()
        self.shutdown_event.set()

    def _start(self):
        print("Connected:", self.consumer.bootstrap_connected())
        print("Subscribed To:", self.consumer.subscription())

        try:
            accumulated_events = []
            print("Listening...")
            for msg in self.consumer:
                if msg:
                    print(msg.value)
                    accumulated_events.append(msg.value)
                    if len(accumulated_events) >= THRESHOLD:
                        brahmastra_v2_in_delay.apply_async(
                            kwargs={"events": accumulated_events}, queue="statistics"
                        )

        except KeyboardInterrupt:
            pass

        finally:
            self.stop()


async_consumer = AsyncConsumer()
