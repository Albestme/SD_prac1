import redis
from time import sleep
import pika

# Connect to Redis
client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

queue_name = "insults"

# Send multiple insults
tasks = ["tonto", "comemierda", "subnormal", "imbécil"]

for task in tasks:
    client.rpush(queue_name, task)
    print(f"Produced: {task}")
    sleep(1)  # Simulating a delay in task production
