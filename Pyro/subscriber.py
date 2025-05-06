import Pyro4
import threading
import time

@Pyro4.expose
class InsultSubscriber:
    def __init__(self, subscriber_id):
        self.subscriber_id = subscriber_id

    def receive_insult(self, insult):
        """Callback method called by the insult service"""
        print(f"Subscriber {self.subscriber_id} received insult: {insult}")


def register_subscriber(subscriber_id):
    ns = Pyro4.locateNS()
    insult_service = Pyro4.Proxy(ns.lookup("insult.service"))

    with Pyro4.Daemon() as daemon:
        observer = InsultSubscriber(subscriber_id)
        observer_uri = daemon.register(observer)  # Get remote URI

        insult_service.register_subscriber(observer_uri)  # Register observer with the observable

        print(f"Subscriber registered with URI: {observer_uri}")
        print("🔄 Waiting for notifications...")

        daemon.requestLoop()  # Keep the observer running to receive updates