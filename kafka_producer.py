from aiokafka import AIOKafkaProducer
import json


async def send_one(message: str):
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        await producer.send_and_wait("quickstart-events", json.dumps(message).encode())
    finally:
        await producer.stop()
