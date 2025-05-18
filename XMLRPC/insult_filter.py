import xmlrpc.client
import threading
from time import sleep
from xmlrpc.server import SimpleXMLRPCServer
import sys
import os


class InsultFilter:
    def __init__(self, insult_service=xmlrpc.client.ServerProxy("http://localhost:8000")):
        # Connection to the InsultService
        self.insult_service = insult_service

        # Storage for filtered texts
        self._filter_queue = []
        self._filtered_results = []

        self.calls_count = 0

        # Start worker thread to process the queue
        threading.Thread(target=self._process_queue, daemon=True).start()

    def filter_text(self, text):
        """Replace insults in text with CENSORED"""
        filtered = text
        insults = self.insult_service.list_insults()
        for insult in insults:
            filtered = filtered.replace(insult, "CENSORED")
        return filtered

    def append_text_filtering_work_queue(self, text):
        """Add text to the filter queue (work queue pattern)"""
        self._filter_queue.append(text)
        self.calls_count += 1
        print(f"{os.getpid()}: {self.calls_count}")
        return "Text added to work queue"

    def list_filtered_results(self):
        """Return all filtered texts"""
        return self._filtered_results

    def _process_queue(self):
        """Worker that processes the queue in background"""
        while True:
            # Process any texts in the queue
            if self._filter_queue:
                text = self._filter_queue.pop(0)
                filtered = self.filter_text(text)
                self._filtered_results.append(filtered)
                print(f"Filtered: '{text}' → '{filtered}'")
            sleep(60)


if __name__ == "__main__":
    # Create the filter service
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    insult_service_port = int(sys.argv[2]) if len(sys.argv) > 1 else 8001
    insult_service = xmlrpc.client.ServerProxy(f"http://localhost:{insult_service_port}")
    filter_service = InsultFilter(insult_service)
    # Create and start XML-RPC server
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    server.register_instance(filter_service)
    print(f"InsultFilter service running on port {port}...")

    # Start the server
    server.serve_forever()


