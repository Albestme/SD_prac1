import time
import csv
import redis
import xmlrpc.client
import Pyro4
from benchmark_decorator import InsultServiceDecorator, FilterServiceDecorator
from XMLRPC.insult_service import InsultService as Xmlrpc_Insult_Service
from XMLRPC.insult_filter import InsultFilter as Xmlrpc_Filter_Service
from Redis.insult_service import InsultService as Redis_Insult_Service
from Redis.insult_filter import InsultFilter as Redis_Filter_Service
from RabbitMQ_Redis.insult_service import InsultService as RabbitMQ_Insult_Service
from RabbitMQ_Redis.insult_filter import InsultFilter as RabbitMQ_Filter_Service
from Pyro.insult_service import InsultService as Pyro_Insult_Service
from Pyro.insult_filter import FilterService as Pyro_Filter_Service


def benchmark_single(module_names, clients, iterations):
    for module_name in module_names:
        print("starting benchmark for module:", module_name)
        if module_name == 'XMLRPC':
            insult_service_proxy = xmlrpc.client.ServerProxy('http://localhost:8000')
            filter_service_proxy = xmlrpc.client.ServerProxy('http://localhost:8001')
            (InsultServiceDecorator(insult_service_proxy, 'XMLRPC', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(filter_service_proxy, 'XMLRPC', 'single_node')
            .stress_filter_service(num_clients=clients, iterations_per_client=iterations))

        elif module_name == 'Pyro':
            ns = Pyro4.locateNS()
            insult_service_proxy = Pyro4.Proxy(ns.lookup("insult.service"))
            filter_service_proxy = Pyro4.Proxy(ns.lookup("filter.service"))
            (InsultServiceDecorator(insult_service_proxy, 'Pyro', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(filter_service_proxy, 'Pyro', 'single_node')
            .stress_filter_service(num_clients=clients, iterations_per_client=iterations))

        elif module_name == 'Redis':
            (InsultServiceDecorator(Redis_Insult_Service(), 'Redis', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(Redis_Filter_Service(), 'Redis', 'single_node')
            .stress_filter_service(num_clients=clients, iterations_per_client=iterations))

        elif module_name == 'RabbitMQ_Redis':
            (InsultServiceDecorator(RabbitMQ_Insult_Service(), 'RabbitMQ_Redis', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(RabbitMQ_Filter_Service(), 'RabbitMQ_Redis', 'single_node')
            .stress_filter_service(num_clients=clients, iterations_per_client=iterations))


if __name__ == "__main__":
    # Define the module name
    architectures = ['XMLRPC']

    benchmark_single(architectures, 3, 10000)

