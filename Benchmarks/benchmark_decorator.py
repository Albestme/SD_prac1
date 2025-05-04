import time
import multiprocessing
import random
from XMLRPC.insult_service import InsultService as Xmlrpc_Insult_Service
import csv


def write_csv(mode, architecture, num_clients, iterations_per_client, elapsed_time):
    with open(f'{mode}.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([architecture, num_clients, iterations_per_client, elapsed_time])


class BenchmarkDecorator:
    def __init__(self):
        self.start_time = None
        self.end_time = None


class InsultServiceDecorator(BenchmarkDecorator):
    def __init__(self, service):
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

    def stress_insult_service(self, mode, architecture, num_clients=3, iterations_per_client=2500000):
        self.start_time = time.time()

        self.create_clients(num_clients, iterations_per_client)
        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        write_csv(mode, architecture, num_clients, iterations_per_client, total_time)

        print(f'Elapsed time: {total_time} seconds')
        return total_time

    def create_clients(self, num_clients, iterations_per_client):
        processes = []
        for i in range(num_clients):
            processes.append(multiprocessing.Process(target=self.stressfull_client, args=(iterations_per_client, )))
            processes[i].start()

        for process in processes:
            process.join()


if __name__ == "__main__":
    InsultServiceDecorator(Xmlrpc_Insult_Service()).stress_insult_service('single_node', 'XMLRPC', num_clients=10, iterations_per_client=10000000)





