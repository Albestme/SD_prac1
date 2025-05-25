import Pyro4
import threading
from time import sleep
import sys

Pyro4.config.REQUIRE_EXPOSE = True

@Pyro4.expose
class FilterService:
    def __init__(self, insult_service_number=''):
        self.filtered_texts = []
        self.work_queue = []
        self.request_counter = 0
        self.insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']

        # Start worker thread to process the queue
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()


    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        for insult in self.insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def append_text_filtering_work_queue(self, text):
        """Add text to the filter queue (work queue pattern)"""
        self.work_queue.append(text)
        return "Text added to work queue"

    def list_filtered_results(self):
        """Return all filtered texts"""
        return self.filtered_texts

    def get_processed_requests(self):
        """Return the number of processed requests"""
        return self.request_counter

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            if self.work_queue:
                text = self.work_queue.pop(0)
                filtered = self.filter_text(text)
                self.filtered_texts.append(filtered)
                print(f"Filtered: '{text}' → '{filtered}'")
            sleep(0.01)


if __name__ == "__main__":
    service_number = int(sys.argv[1]) if len(sys.argv) > 1 else ''
    # Create and register the filter service
    filter_service = FilterService(service_number)

    # Create a daemon
    daemon = Pyro4.Daemon()

    # Register the object with Pyro
    uri = daemon.register(filter_service)

    # Register with the name server
    ns = Pyro4.locateNS()
    ns.register(f"filter.service{service_number}", uri)

    print(f"FilterService running with URI: {uri}")
    print("Starting request loop...")

    # Start the request loop
    daemon.requestLoop()