import time
import csv
import redis
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
        if module_name == 'XMLRPC':
            (InsultServiceDecorator(Xmlrpc_Insult_Service(), 'XMLRPC', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(Xmlrpc_Filter_Service(), 'XMLRPC', 'single_node')
            .stress_filter_service(num_clients=clients, iterations_per_client=iterations))
        elif module_name == 'Pyro':
            (InsultServiceDecorator(Pyro_Insult_Service(), 'Pyro', 'single_node')
            .stress_insult_service(num_clients=clients, iterations_per_client=iterations))
            (FilterServiceDecorator(Pyro_Filter_Service(), 'Pyro', 'single_node')
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
    architectures = ['XMLRPC', 'Redis', 'RabbitMQ_Redis', 'Pyro']

    benchmark_single(architectures, 3, 10000000)

