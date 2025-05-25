
class LoadBalancer:
    def __init__(self, architecture, test_type):
        self.architecture = architecture
        self.test_type = test_type
        self.insult_services = []
        self.filter_services = []
        self.insult_index = 0
        self.filter_index = 0

    def register_insult_service(self, service):
        self.insult_services.append(service)

    def register_filter_service(self, service):
        self.filter_services.append(service)

    def get_insult_service_round_robin(self):
        if not self.insult_services:
            raise ValueError("No insult services available")
        service = self.insult_services[self.insult_index]
        self.insult_index = (self.insult_index + 1) % len(self.insult_services)
        return service

    def get_filter_service_round_robin(self):
        if not self.filter_services:
            raise ValueError("No filter services available")
        service = self.filter_services[self.filter_index]
        self.filter_index = (self.filter_index + 1) % len(self.filter_services)
        return service
