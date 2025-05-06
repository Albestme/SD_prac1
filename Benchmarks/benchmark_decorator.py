import time
import multiprocessing
import random
from XMLRPC.insult_service import InsultService as Xmlrpc_Insult_Service
from XMLRPC.insult_filter import InsultFilter as Xmlrpc_Filter_Service
import csv
from abc import ABC, abstractmethod

def write_csv(mode, architecture, num_clients, iterations_per_client, elapsed_time):
    with open(f'{mode}.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([architecture, num_clients, iterations_per_client, elapsed_time])


class BenchmarkDecorator(ABC):
    def __init__(self, architecture, mode):
        self.start_time = None
        self.end_time = None
        self.architecture = architecture    # XMLRPC, Redis, RabbitMQ_Redis, Pyro
        self.mode = mode                    # single_node, multi_node_static, multi_node_dynamic

    def create_clients(self, num_clients, iterations_per_client):
        processes = []
        for i in range(num_clients):
            processes.append(multiprocessing.Process(target=self.stressfull_client, args=(iterations_per_client, )))
            processes[i].start()

        for process in processes:
            process.join()

    @abstractmethod
    def stressfull_client(self, iterations):
        pass


class InsultServiceDecorator(BenchmarkDecorator):
    def __init__(self, service, architecture, mode):
        super().__init__(architecture, mode)
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
        for _ in range(iterations):
            self.insult_service.add_insult(random.choice(self.insults))

    def stress_insult_service(self, num_clients=3, iterations_per_client=2500000):
        self.start_time = time.time()

        self.create_clients(num_clients, iterations_per_client)
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        write_csv(self.mode, self.architecture, num_clients, iterations_per_client, total_time)

        print(f'Elapsed time: {total_time} seconds')
        return total_time


class FilterServiceDecorator(BenchmarkDecorator):
    def __init__(self, service, architecture, mode):
        super().__init__(architecture, mode)
        self.filter_service = service
        self.texts = [
                        'JAJAJA, Im sorry, but you are dumb and stupid',
                        'I love to see a moron cry',
                        'stupid idiot I hate you',
                        'Only a groomer would say that',
                        'I love to way acrotomophile cry',
                        'Que viva España',
                        'You are an air head and an accident',
                        'I love how strawberries taste'
                      ]

    def stressfull_client(self, iterations):
        for _ in range(iterations):
            self.filter_service.append_text_filtering_work_queue(random.choice(self.texts))

    def stress_filter_service(self, num_clients=3, iterations_per_client=2500000):
        self.start_time = time.time()
        self.create_clients(num_clients, iterations_per_client)
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        write_csv(self.mode, self.architecture, num_clients, iterations_per_client, total_time)

        print(f'Elapsed time: {total_time} seconds')
        return total_time




if __name__ == "__main__":
    (InsultServiceDecorator(Xmlrpc_Insult_Service(), 'XMLRPC', 'single_node' ).
     stress_insult_service(num_clients=10, iterations_per_client=10000000))

    (FilterServiceDecorator(Xmlrpc_Filter_Service(), 'XMLRPC', 'single_node').
     stress_filter_service(num_clients=10, iterations_per_client=10000000))





