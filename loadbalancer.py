import random
import time
from Benchmarks.benchmark_decorator import InsultServiceDecorator, FilterServiceDecorator
import multiprocessing
from Benchmarks.benchmark_decorator import write_csv

# Proxy that attends the requests of the clients
class LoadBalancer:
    insult_services = []
    filter_services = []
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
    insults = ['dumb',
                        'moron',
                        'stupid',
                        'idiot',
                        'groomer',
                        'acrotomophile',
                        'air head',
                        'accident'
                        ]

    def __init__(self, architecture, mode):
        self.architecture = architecture
        self.mode = mode

    def register_insult_service(self, service):
        service = InsultServiceDecorator(service, self.architecture, self.mode)
        self.insult_services.append(service)

    def register_filter_service(self, service):
        service = FilterServiceDecorator(service, self.architecture, self.mode)
        self.filter_services.append(service)

    def add_insult(self, insult):
        service = random.choice(self.insult_services)
        return service.add_insult(insult)

    def append_text_filtering_work_queue(self, text):
        service = random.choice(self.filter_services)
        return service.append_text_filtering_work_queue(text)

    def stressfull_client(self, iterations, service_type):
        if service_type == 'insult':
            for _ in range(iterations):
                service = random.choice(self.insult_services).insult_service
                service.add_insult(random.choice(self.insults))
        elif service_type == 'filter':
            for _ in range(iterations):
                service = random.choice(self.filter_services).filter_service
                service.append_text_filtering_work_queue(random.choice(self.texts))

    def stress_insult_service(self, num_clients, iterations_per_client):
        start_time = time.time()
        processes = []
        for i in range(num_clients):
            processes.append(
                multiprocessing.Process(target=self.stressfull_client, args=(iterations_per_client, 'insult', )))
            processes[i].start()

        for p in processes:
            p.join()
        end_time = time.time()
        total_time = end_time - start_time
        write_csv(self.mode, self.architecture, num_clients, iterations_per_client, total_time, 'insult_service')

    def stress_filter_service(self, num_clients, iterations_per_client):
        start_time = time.time()
        processes = []
        for i in range(num_clients):
            processes.append(
                multiprocessing.Process(target=self.stressfull_client, args=(iterations_per_client, 'filter', )))
            processes[i].start()

        for p in processes:
            p.join()
        end_time = time.time()
        total_time = end_time - start_time
        write_csv(self.mode, self.architecture, num_clients, iterations_per_client, total_time, 'filter_service')