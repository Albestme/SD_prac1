import time
import csv
from benchmark_decorator import InsultServiceDecorator
from XMLRPC.insult_service import InsultService as Xmlrpc_Insult_Service
from Redis.insult_service import InsultService as Redis_Insult_Service
from RabbitMQ_Redis.insult_service import InsultService as RabbitMQ_Insult_Service
from Pyro.InsultService import InsultService as Pyro_Insult_Service


def write_csv(architecture, num_clients, iterations_per_client, elapsed_time):
    with open('benchmark_results.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([architecture, num_clients, iterations_per_client, elapsed_time])


def benchmark_single(module_names):
    for module_name in module_names:
        benchmarker = InsultServiceDecorator(module_name)
        benchmarker.stress_insult_service(module_name, num_clients=3, iterations_per_client=2500000)



if __name__ == "__main__":
    # Define the module name
    module_names = ['XMLRPC', 'Redis', 'RabbitMQ_Redis', 'Pyro']

    # Start the benchmark
    start_time = time.time()
    benchmark_single(module_names)
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Write the result to a CSV file
    with open('benchmark_results.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([module_names, elapsed_time])

