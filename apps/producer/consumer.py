from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "music.play_events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="music-consumer"
)

print("Listening to topic: music.play_events")
for message in consumer:
    print("Consumed:", message.value)
