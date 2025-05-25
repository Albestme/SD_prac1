import multiprocessing
import random
from mixed.mixed_client import MixedClient as Client
from mixed.scaling_manager import ServerScalingManager as ServerManager
from time import sleep


texts = [
    'JAJAJA, Im sorry, but you are dumb and stupid',
    'I love to see a moron cry',
    'stupid idiot I hate you',
    'Only a groomer would say that',
    'I love to way acrotomophile cry',
    'Que viva España',
    'You are an air head and an accident',
    'I love how strawberries taste'
]
insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']


def fill_queue(iterations):
    def append(requests):
        client = Client()
        for i in range(requests):
            client.add_insult(random.choice(insults))
            client.append_text_filtering_work_queue(random.choice(texts))
            print(i)

        print(f"Sent {iterations} messages to the server.")
    processes = []
    for _ in range(10):
        processes.append(multiprocessing.Process(target=append, args=(iterations,)))
        processes[-1].start()
    for i in range(len(processes)):
        processes[i].join()

def process_queue():
    server_manager = multiprocessing.Process(target=ServerManager)
    server_manager.start()
    while True:
        sleep(10)




if __name__ == '__main__':
    #fill_queue(50000)
    process_queue()