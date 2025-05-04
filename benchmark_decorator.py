import time
import multiprocessing
import random
from XMLRPC.insult_service import InsultService as Xmlrpc_Insult_Service
from Redis.insult_service import InsultService as Redis_Insult_Service
from RabbitMQ_Redis.insult_service import InsultService as RabbitMQ_Insult_Service
from Pyro.InsultService import InsultService as Pyro_Insult_Service
import matplotlib.pyplot as plt
import csv


class BenchmarkDecorator:
    def __init__(self):
        self.start_time = None
        self.end_time = None


class InsultServiceDecorator(BenchmarkDecorator):
    def __init__(self, service, num_services=1):
        super().__init__()
        self.insult_service = service
        self.insults = ['dumb',
                        'moron',
                        'stupid',
                        'idiot',
                        'groomer',
                        'acrotomophile',
                        'air head',
                        'accident'
                        ]

    def stressfull_client(self, iterations):
        for _ in range(0, iterations):
            self.insult_service.add_insult(random.choice(self.insults))

    def stress_insult_service(self, architecture, num_clients=3, iterations_per_client=2500000):
        self.start_time = time.time()

        self.create_clients()
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        print(f'Elapsed time: {total_time} seconds')
        return total_time

    def create_clients(self):
        processes = []
        for i in range(3):
            processes.append(multiprocessing.Process(target=self.stressfull_client, args=(2500000, )))
            processes[i].start()

        for process in processes:
            process.join()


if __name__ == "__main__":
    InsultServiceDecorator(Xmlrpc_Insult_Service()).stress_insult_service()





