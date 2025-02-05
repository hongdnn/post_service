import aiokafka

from src import Config


class KafkaProducer:
    def __init__(self):
        self.producer = None

    async def connect(self):
        self.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
        )
        await self.producer.start()

    async def send_message(self, topic, message):
        if not self.producer:
            await self.connect()

        await self.producer.send_and_wait(topic, message.encode('utf-8'))

    async def close(self):
        if self.producer:
            await self.producer.stop()


