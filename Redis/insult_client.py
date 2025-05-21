import redis


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.insult_list = "insult_list"
        self.insult_queue = 'insult_work_queue'
        self.broadcast_chanel = "broadcast_channel"
        self.filtered_queue = 'text_filtered_queue'
        self.text_work_queue = 'text_work_queue'

    def get_insults(self):
        """Get all insults from the Redis list"""
        return self.client.lrange(self.insult_list, 0, -1)

    def add_insults(self, insult):
        """Add a new insult to the Redis list"""
        self.client.rpush(self.insult_queue, insult)
        return f"Insult added to Redis list: {insult}"

    def append_text_filtering_work_queue(self, text):
        """Append text to the work queue for filtering"""
        self.client.rpush(self.text_work_queue, text)
        return f"Text appended to work queue: {text}"

    def list_filtered_results(self):
        """List all filtered results"""
        return self.client.lrange(self.filtered_queue, 0, -1)
