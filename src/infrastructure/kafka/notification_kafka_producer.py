import json

from src.constants.notification_type import NotificationType
from src.domain.entities.reaction import Reaction
from src.infrastructure.kafka.kafka_producer import KafkaProducer
from src.infrastructure.kafka.kafka_topic import KafkaTopic


class NotificationKafkaProducer(KafkaProducer):
    async def post_message(self, receiver_id: str, data: any, notification_type: NotificationType):
        data = self.handle_data(receiver_id, data, notification_type)
        await self.send_message(KafkaTopic.NOTIFICATION.value, json.dumps({
            'data': data
        }))

    @staticmethod
    def handle_data(receiver_id: str, data: any, notification_type: NotificationType) -> any:
        data_dict = None
        if isinstance(data, Reaction):
            data_dict = {
                'type': notification_type.value,
                'user_id': receiver_id,
                'created_by': data.user_id,
                'post_id': data.post_id,
                'target_id': data.id,
                'created_date': data.created_date.isoformat()
            }
        return data_dict