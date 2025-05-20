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
from time import sleep


# -------------------------------
# Client Worker Function
# -------------------------------
def stressfull_client(client_id, module_name, nodes, iterations, service_type):
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

    # Connect services inside the client process
    lb = connect_servers(module_name, nodes)

    if not lb:
        print(f"Client {client_id}: Failed to connect to servers.")
        return

    start_time = time.time()

    if service_type == 'insult':
        for _ in range(iterations):
            try:
                service = lb.get_insult_service_round_robin()
                service.add_insult(random.choice(insults))
            except Exception as e:
                sleep(0.01)
                print(f"Client {client_id}: Error adding insult: {e}")
                service = lb.get_insult_service_round_robin()
                service.add_insult(random.choice(insults))

    elif service_type == 'filter':
        for _ in range(iterations):
            try:
                service = lb.get_filter_service_round_robin()
                service.append_text_filtering_work_queue(random.choice(texts))
            except Exception as e:
                sleep(0.01)
                print(f"Client {client_id}: Error filtering text: {e}")
                service = lb.get_filter_service_round_robin()
                service.append_text_filtering_work_queue(random.choice(texts))

    end_time = time.time()
    print(f"Client {client_id} completed {iterations} iterations in {end_time - start_time:.4f}s")


# -------------------------------
# Benchmark Execution
# -------------------------------
def stress_service(module_name, nodes, iterations, service_type, num_clients, mode):
    start_time = time.time()
    processes = []

    for i in range(num_clients):
        p = multiprocessing.Process(
            target=stressfull_client,
            args=(i, module_name, nodes, iterations, service_type)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time for {num_clients} clients: {total_time:.2f}s")
    write_csv(mode, module_name, num_clients, iterations, total_time, service_type, nodes)


# -------------------------------
# Benchmark Orchestrator
# -------------------------------
def benchmark_multi_node_static(module_names, mode, clients, iterations, nodes):
    for module_name in module_names:
        print("Starting benchmark for module:", module_name)
        if module_name == 'XMLRPC':
            stress_service(module_name, nodes, iterations, 'insult', clients, mode)
            stress_service(module_name, nodes, iterations, 'filter', clients, mode)

        elif module_name == 'Pyro':
            stress_service(module_name, nodes, iterations, 'insult', clients, mode)
            stress_service(module_name, nodes, iterations, 'filter', clients, mode)

        elif module_name == 'Redis':
            stress_service(module_name, nodes, iterations, 'insult', clients, mode)
            stress_service(module_name, nodes, iterations, 'filter', clients, mode)

        elif module_name == 'RabbitMQ_Redis':
            stress_service(module_name, nodes, iterations, 'insult', clients, mode)
            stress_service(module_name, nodes, iterations, 'filter', clients, mode)


# -------------------------------
# Server Connection Logic (Now Process-safe)
# -------------------------------
def connect_servers(module_name, nodes):
    if module_name == 'XMLRPC':
        lb = LoadBalancer('XMLRPC', 'multi_node_static')

        for j in range(nodes):
            insult_proxy = xmlrpc.client.ServerProxy(f'http://localhost:{8000 + j}', allow_none=True)
            filter_proxy = xmlrpc.client.ServerProxy(f'http://localhost:{8003 + j}', allow_none=True)

            lb.register_insult_service(insult_proxy)
            lb.register_filter_service(filter_proxy)

        return lb

    elif module_name == 'Pyro':
        lb = LoadBalancer('Pyro', 'multi_node_static')
        ns = Pyro4.locateNS()
        for i in range(nodes):
            insult_proxy = Pyro4.Proxy(ns.lookup(f"insult.service{i}"))
            filter_proxy = Pyro4.Proxy(ns.lookup(f"filter.service{i}"))
            lb.register_insult_service(insult_proxy)
            lb.register_filter_service(filter_proxy)
        return lb

    elif module_name == 'Redis':
        lb = LoadBalancer('Redis', 'multi_node_static')

        lb.register_insult_service(Redis_Insult_Service())
        lb.register_filter_service(Redis_Filter_Service())
        return lb

    elif module_name == 'RabbitMQ_Redis':
        lb = LoadBalancer('RabbitMQ_Redis', 'multi_node_static')
        for i in range(nodes):
            lb.register_insult_service(RabbitMQ_Insult_Service())
            lb.register_filter_service(RabbitMQ_Filter_Service())
        return lb

    return None


# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == '__main__':
    architectures = ['Redis']
    data = 'multiple_node_static'
    benchmark_multi_node_static(architectures, data, clients=1, iterations=200000, nodes=3)