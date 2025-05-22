import xmlrpc.client
import Pyro4
from Redis.redis_client import RedisClient as RedisClient
from Redis.insult_service import start_insult_server as redis_insult_server
from Redis.insult_filter import start_insult_filter as redis_filter_server
from loadbalancer import LoadBalancer
import multiprocessing
import time
from Benchmarks.benchmark_decorator import write_csv
import random
from time import sleep
from multiprocessing import Value


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

    if module_name == 'Redis':
        redis_client = RedisClient()
        processes = []
        if service_type == 'insult':
            for _ in range(iterations):
                redis_client.add_insult(random.choice(insults))
            start_time = time.time()
            for i in range(nodes):
                processes.append(multiprocessing.Process(target=redis_insult_server))
                processes[i].start()
            redis_client.wait_insult_requests_processing(iterations)

        else:
            for _ in range(iterations):
                redis_client.append_text_filtering_work_queue(random.choice(texts))
            start_time = time.time()
            for i in range(nodes):
                processes.append(multiprocessing.Process(target=redis_filter_server))
                processes[i].start()
            redis_client.wait_filter_requests_processing(iterations)

        for p in processes:
            p.terminate()


    if module_name == 'XMLRPC' or module_name == 'Pyro':
        lb = connect_servers(module_name, nodes)

        if not lb:
            print(f"Client {client_id}: Failed to connect to servers.")
            return None

        start_time = time.time()
        if service_type == 'insult':
            for i in range(iterations):
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
        lb.register_insult_service(RedisClient())
        lb.register_filter_service(RedisClient())
        return lb

    elif module_name == 'RabbitMQ_Redis':
        lb = LoadBalancer('RabbitMQ_Redis', 'multi_node_static')
        return lb

    return None


# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == '__main__':
    architectures = ['Redis']
    data = 'redis_data'
    benchmark_multi_node_static(architectures, data, clients=1, iterations=30000, nodes=3)