from xmlrpc.server import SimpleXMLRPCServer
import threading
from time import sleep
import random
import xmlrpc.client


class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = []
        threading.Thread(target=self._broadcast_insults, daemon=True).start()

    def add_insult(self, insult):
        """Add an insult if not already in the list"""
        self.insults.add(insult)

    def list_insults(self):
        """Return all stored insults"""
        return list(self.insults)

    def register_subscriber(self, subscriber_url):
        """Register a subscriber URL to receive broadcasts"""
        if subscriber_url not in self.subscribers:
            self.subscribers.append(subscriber_url)
            print(f"Registered subscriber at {subscriber_url}")
            return True
        return False

    def unregister_subscriber(self, subscriber_url):
        """Remove a subscriber"""
        if subscriber_url in self.subscribers:
            self.subscribers.remove(subscriber_url)
            return True
        return False

    def _broadcast_insults(self):
        """Periodically broadcast random insults to subscribers"""
        while True:
            if self.insults and self.subscribers:
                insult = random.choice(list(self.insults))
                print(f"Broadcasting insult: {insult} to {len(self.subscribers)} subscribers")

                # Broadcast to all subscribers
                for subscriber_url in self.subscribers[:]:
                    try:
                        proxy = xmlrpc.client.ServerProxy(subscriber_url)
                        proxy.receive_insult(insult)
                    except Exception as e:
                        print(f"Error broadcasting to {subscriber_url}: {e}")
            sleep(5)


if __name__ == "__main__":
    # Create and start XML-RPC server
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    server.register_instance(InsultService())
    print("InsultService running on port 8000...")
    server.serve_forever()