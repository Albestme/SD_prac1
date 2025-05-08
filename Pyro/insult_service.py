import Pyro4
import random
import threading
from time import sleep


Pyro4.config.REQUIRE_EXPOSE = True

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class InsultService:
    def __init__(self):
        self.insults = []
        self.subscribers = []

        # Start automatic broadcast thread
        self.broadcast_thread = threading.Thread(target=self._broadcast_random_insult)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()

    def add_insult(self, insult):
        if insult in self.insults:
            return f"Insult service already has {insult} in it's list"

        self.insults.append(insult)
        return f"Insult service added {insult} to it's list"

    def get_insults(self):
        return self.insults

    def register_subscriber(self, subscriber_uri):
        """Register a subscriber to receive insults"""
        subscriber = InsultSubscriber(subscriber_uri)
        self.subscribers.append(subscriber)
        print(f"Observer {subscriber_uri} registered")

    def notify_subscribers(self, insult):
        """Notify all registered subscribers with the given Insult"""
        for subscriber in self.subscribers:
            try:
                subscriber.receive_insult(insult)
            except Exception as e:
                print(f"Failed to notify subscriber: {e}")
                print(f"Removing subscriber {subscriber._pyroUri} from the list")
                self.subscribers.remove(subscriber)

    def unregister_observer(self, observer_uri):
        """Unregister an observer."""
        self.subscribers = [obs for obs in self.subscribers if obs._pyroUri != observer_uri]
        print(f"Observer {observer_uri} unregistered.")

    def _broadcast_random_insult(self):
        """Periodically broadcast random insults"""
        while True:
            sleep(5)  # Every 5 seconds
            if self.insults and self.subscribers:
                insult = random.choice(self.insults)
                print(f"Broadcasting insult: {insult}")
                self.notify_subscribers(insult)

@Pyro4.expose
class InsultSubscriber:
    def __init__(self, subscriber_id):
        self.subscriber_id = subscriber_id

    def receive_insult(self, insult):
        """Callback method called by the insult service"""
        print(f"Subscriber {self.subscriber_id} received insult: {insult}")

if __name__ == "__main__":
    daemon = Pyro4.Daemon()  # Create Pyro daemon
    ns = Pyro4.locateNS()  # Locate name server
    uri = daemon.register(InsultService())  # Register InsultService instance
    ns.register("insult.service", uri)  # Register with a unique name

    print("Insult server running...")
    daemon.requestLoop()  # Keep server running