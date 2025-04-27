import Pyro4
from time import sleep
import random
from threading import Thread
from Subscriber import register_subscriber


if __name__ == "__main__":
    insults = ["stupid", "idiot", "fool", "dummy", "moron"]

    ns = Pyro4.locateNS()

    # Connect to the remote services
    insult_service = Pyro4.Proxy(ns.lookup("insult.service"))
    filter_service = Pyro4.Proxy(ns.lookup("filter.service"))

    # Start subscribers
    for i in range(1, 4):
        Thread(target=register_subscriber, args=(f"Subscriber-{i}",)).start()
        sleep(1)

    for insult in insults:
        insult_service.add_insult(insult)

    print(insult_service.get_insults())

    texts = [
        "You are so stupid!",
        "What a fool you are!",
        "Don't be such an idiot!",
        "You are a dummy!",
        "You moron!",
        "You are a genius!",
        "Life is great!"
    ]

    for _ in range(10):
        filter_service.append_text_filtering_work_queue(random.choice(texts))
        sleep(0.3)








