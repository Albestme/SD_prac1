import Pyro4
import threading
from time import sleep

Pyro4.config.REQUIRE_EXPOSE = True

@Pyro4.expose
class FilterService:
    def __init__(self):
        self.filtered_texts = []
        self.work_queue = []
        self.insult_service = None
        print(self.connect_to_insult_service())

        # Start worker thread to process the queue
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def connect_to_insult_service(self):
        # Connect to InsultService via the name server
        ns = Pyro4.locateNS()
        uri = ns.lookup("insult.service")
        self.insult_service = Pyro4.Proxy(uri)
        return "Connected to insult service"

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        if not self.insult_service:
            self.connect_to_insult_service()

        filtered = text
        insults = self.insult_service.list_insults()
        for insult in insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def append_text_filtering_work_queue(self, text):
        """Add text to the filter queue (work queue pattern)"""
        self.work_queue.append(text)
        return "Text added to work queue"

    def list_filtered_results(self):
        """Return all filtered texts"""
        return self.filtered_texts

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            if self.work_queue:
                text = self.work_queue.pop(0)
                filtered = self.filter_text(text)
                self.filtered_texts.append(filtered)
                print(f"Filtered: '{text}' → '{filtered}'")
            sleep(5)  # Check for new work every 5 seconds


if __name__ == "__main__":
    # Create and register the filter service
    filter_service = FilterService()

    # Create a daemon
    daemon = Pyro4.Daemon()

    # Register the object with Pyro
    uri = daemon.register(filter_service)

    # Register with the name server
    ns = Pyro4.locateNS()
    ns.register("filter.service", uri)

    print(f"FilterService running with URI: {uri}")
    print("Starting request loop...")

    # Start the request loop
    daemon.requestLoop()