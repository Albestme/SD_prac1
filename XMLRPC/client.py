import random
import xmlrpc.client
from XMLRPC.subscriber import InsultSubscriber

if __name__ == '__main__':
    insult_service= xmlrpc.client.ServerProxy('http://localhost:8000')
    filter_service = xmlrpc.client.ServerProxy('http://localhost:8001')

    insults = ["tonto", "Montoya", "piltrafa", "seguidor promedio de Alexelcapo"]

    for insult in insults:
        insult_service.add_insult(insult)

    print(f"Insult list = {insult_service.list_insults()}")

    InsultSubscriber(1)
    InsultSubscriber(2)
    InsultSubscriber(3)

    texts = [
        "Eres un tonto",
        "Eres un Montoya",
        "Eres un piltrafa",
        "Eres un seguidor promedio de Alexelcapo",
        "Montoya es seguidor promedio de Alexelcapo",
        "Que viva ESPAÑA"
    ]

    for i in range(10):
        print(filter_service.append_text_filtering_work_queue(random.choice(texts)))

    print(insult_service.list_insults())
    print(filter_service.list_filtered_results())