import redis
import random
from time import sleep
from insult_service import InsultService
from insult_filter import InsultFilter

if __name__ == "__main__":
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    queue_name = 'insults'
    insult_service = InsultService()
    filter_service = InsultFilter()

    insults = ["idiot", "fool", "moron", "dummy", "blockhead", "nincompoop", "dimwit", "dunce", "nitwit", "bonehead"]

    for insult in insults:
        insult_service.add_insult(insult)

    print(insult_service.get_insults())

    for i in range(3):
        insult_service.register_subscriber(i)

    texts = [
        "You are a fool",
        "You are a genius",
        "You are an idiot",
        "You are a smart person",
        "You are a moron"
    ]

    for i in range(10):
        filter_service.append_text_filtering_work_queue(random.choice(texts))

    print(insult_service.get_insults())
    sleep(6)
    print(filter_service.list_filtered_results())