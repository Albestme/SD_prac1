import xmlrpc.client
import Pyro4
from benchmark_decorator import InsultServiceDecorator, FilterServiceDecorator
from Redis.insult_service import InsultService as Redis_Insult_Service
from Redis.insult_filter import InsultFilter as Redis_Filter_Service
from RabbitMQ_Redis.insult_service import InsultService as RabbitMQ_Insult_Service
from RabbitMQ_Redis.insult_filter import InsultFilter as RabbitMQ_Filter_Service
from loadbalancer import LoadBalancer
import multiprocessing
import time
from Benchmarks.benchmark_decorator import write_csv
import random
import os


def stressfull_client(lb, iterations, service_type):
    start_time = time.time()
    lenght = len(lb.insult_services)
    if service_type == 'insult':
        for i in range(iterations):
            service = lb.insult_services[i % lenght].insult_service
            service.add_insult(random.choice(lb.insults))
    elif service_type == 'filter':
        for i in range(iterations):
            service = lb.filter_services[i % lenght].filter_service
            service.append_text_filtering_work_queue(random.choice(lb.texts))

    end_time = time.time()
    print(f'{os.getpid()}: ' + str(end_time - start_time))


def stress_service(load_balancers, architecture, iterations_per_client, service_type):
    start_time = time.time()
    processes = []
    base_chunk = iterations_per_client // len(load_balancers)
    remainder = iterations_per_client % len(load_balancers)
    chunks = [base_chunk+remainder, base_chunk, base_chunk]
    for lb, i in zip(load_balancers, range(len(load_balancers))):
        processes.append(
            multiprocessing.Process(target=stressfull_client, args=(lb, chunks[i], service_type)))
        processes[i].start()

    for p in processes:
        p.join()
    end_time = time.time()
    total_time = end_time - start_time
    write_csv('multiple_node_static', architecture, len(load_balancers), iterations_per_client, total_time,
              service_type)



def benchmark_multi_node_static(module_names, clients, iterations, nodes):
    for module_name in module_names:
        print("starting benchmark for module:", module_name)
        if module_name == 'XMLRPC':
            load_balancers = connect_servers(module_name, nodes)
            stress_service(load_balancers, module_name, iterations, 'insult')
            stress_service(load_balancers, module_name, iterations, 'filter')

        elif module_name == 'Pyro':
            lb = connect_servers(module_name, nodes)
            lb.stress_insult_service(clients, iterations)
            lb.stress_filter_service(clients, iterations)

        elif module_name == 'Redis':
            lb = connect_servers(module_name, nodes)
            lb.stress_insult_service(clients, iterations)
            lb.stress_filter_service(clients, iterations)

        elif module_name == 'RabbitMQ_Redis':
            lb = connect_servers(module_name, nodes)
            lb.stress_insult_service(clients, iterations)
            lb.stress_filter_service(clients, iterations)


def connect_servers(module_name, nodes):
    if module_name == 'XMLRPC':
        load_balancers = []
        for i in range(nodes):
            lb = LoadBalancer('XMLRPC', 'multi_node_static')
            load_balancers.append(lb)

        for lb in load_balancers:
            for i in range(nodes):
                insult_service_proxy = xmlrpc.client.ServerProxy(f'http://localhost:{8000 + i}')
                filter_service_proxy = xmlrpc.client.ServerProxy(f'http://localhost:{8003 + i}')
                lb.register_insult_service(insult_service_proxy)
                lb.register_filter_service(filter_service_proxy)
        return load_balancers

    elif module_name == 'Pyro':
        lb = LoadBalancer('Pyro', 'multi_node_static')
        ns = Pyro4.locateNS()
        for i in range(nodes):
            insult_service_proxy = Pyro4.Proxy(ns.lookup(f"insult.service.{i}"))
            filter_service_proxy = Pyro4.Proxy(ns.lookup(f"filter.service.{i}"))
            lb.register_insult_service(insult_service_proxy)
            lb.register_filter_service(filter_service_proxy)
        return lb

    elif module_name == 'Redis':
        lb = LoadBalancer('Redis', 'multi_node_static')
        insult_service = Redis_Insult_Service()
        filter_service = Redis_Filter_Service()
        lb.register_insult_service(insult_service)
        lb.register_filter_service(filter_service)

        return lb

    elif module_name == 'RabbitMQ_Redis':
        lb = LoadBalancer('RabbitMQ_Redis', 'multi_node_static')
        for i in range(nodes):
            insult_service = RabbitMQ_Insult_Service()
            filter_service = RabbitMQ_Filter_Service()
            lb.register_insult_service(insult_service)
            lb.register_filter_service(filter_service)

        return lb

    return None


if __name__ == '__main__':
    # Define the module name
    architectures = ['XMLRPC']

    benchmark_multi_node_static(architectures, 3, 20000, 3)