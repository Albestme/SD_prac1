import redis

def start_subscriber(subscriber_id):
    # Connect to Redis
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    channel_name = "broadcast_channel"

    # Subscribe to channel
    pubsub = client.pubsub()
    pubsub.subscribe(channel_name)

    print(f"{subscriber_id} subscribed to {channel_name}, waiting for messages...")

    # Continuously listen for messages
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Subscriber {subscriber_id} received: {message['data']}")