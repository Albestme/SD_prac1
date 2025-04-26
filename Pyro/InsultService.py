import Pyro4


Pyro4.config.REQUIRE_EXPOSE = True

# python -m Pyro4.naming
# Make the server object remotely accessible
@Pyro4.expose
class InsultService:
    insults = list()
    subscribers = list()

    def add_insult(self, insult):
        if insult in self.insults:
            return f"Insult service already has {insult} in it's list"

        self.insults.append(insult)
        return f"Insult service added {insult} to it's list"

    def get_insults(self):
        return self.insults

    def register_suscriber(self, subscriber):
        if not hasattr(subscriber, 'receive_insult'):
            raise ValueError("Subscriber must have a 'notify' method")

        self.subscribers.append(subscriber)
        return "Subscriber registered successfully"

    def notify_subscribers(self, message):
        for subscriber in self.subscribers:
            try:
                subscriber.receive_insult(message)
            except Exception as e:
                print(f"Failed to notify subscriber: {e}")


if __name__ == "__main__":
    daemon = Pyro4.Daemon()  # Create Pyro daemon
    ns = Pyro4.locateNS()  # Locate name server
    uri = daemon.register(InsultService)  # Register EchoServer
    ns.register("echo.server", uri)  # Register with a unique name

    print("Insult server running...")
    daemon.requestLoop()  # Keep server running
