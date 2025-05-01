import redis
from xmlrpc.server import SimpleXMLRPCServer
from InsultBroadcaster import broadcast
from Subscriber import start_subscriber
import threading


def init_subscriber(subscriber_id):
    threading.Thread(target=start_subscriber, args=(subscriber_id, )).start()


class InsultService:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.key = "insults"

    def add_insult(self, text):
        # Add insult if not already present
        if not self.r.sismember(self.key, text):
            self.r.sadd(self.key, text)
            return f"Added insult: {text}"
        return "Insult already exists"

    def list_insults(self):
        # Return the insults as a list
        return list(self.r.smembers(self.key))

    def broadcast_insults(self):
        # Broadcast the insults using the InsultBroadcaster
        threading.Thread(target=broadcast).start()
        print("Broadcasting insults...")


if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000))
    service = InsultService()
    server.register_instance(service)
    print("XML-RPC server listening on port 8000...")
    service.broadcast_insults()

    for i in range(3):
        init_subscriber(i)

    server.serve_forever()