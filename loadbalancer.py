import os
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
