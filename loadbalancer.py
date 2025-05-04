import random

# Proxy that attends the requests of the clients
# Singleton class
class LoadBalancer:
    _instance = None
    _lock = object()

    def __init__(self):
        # The initialization is done in __new__
        self.filter_services = []
        self.insult_services = []

    def register_insult_service(self, service):
        self.insult_services.append(service)

    def register_filter_service(self, service):
        self.filter_services.append(service)

    def add_insult(self, insult):
        # Randomly select an insult service to handle the request
        service = random.choice(self.insult_services)
        return service.add_insult(insult)

    def append_text_filtering_work_queue(self, text):
        service = random.choice(self.filter_services)
        return service.append_text_filtering_work_queue(text)



