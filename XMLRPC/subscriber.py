import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading
from time import sleep

class InsultSubscriber:
    def __init__(self, subscriber_id):
        self.subscriber_id = subscriber_id
        self.received_insults = set()
        self.port = 8100 + subscriber_id

        # Create an XML-RPC server to receive the broadcasted insults
        # You were creating the server twice
        self.server = SimpleXMLRPCServer(('localhost', self.port), allow_none=True)
        self.server.register_function(self.receive_insult)

        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Register with the InsultService
        self.insult_service = xmlrpc.client.ServerProxy("http://localhost:8000")
        self.subscriber_url = f"http://localhost:{self.port}"
        success = self.insult_service.register_subscriber(self.subscriber_url)
        if success:
            print(f"Subscriber {self.subscriber_id} registered at {self.subscriber_url}")
        threading.Thread(target=self.listen_broadcast).start()

    def receive_insult(self, insult):
        """Callback method that will be called by the InsultService"""
        if isinstance(insult, bytes):
            insult = insult.decode("utf-8")
        print(f"Subscriber {self.subscriber_id} received insult: {insult}")
        self.received_insults.add(insult)
        return True

    def listen_broadcast(self):
        """Keep the server running to listen for insults"""
        print(f"Subscriber {self.subscriber_id} listening on port {self.port}")
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            print(f"Subscriber {self.subscriber_id} shutting down")


if __name__ == "__main__":
    import sys
    subscriber_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    subscriber = InsultSubscriber(subscriber_id)

