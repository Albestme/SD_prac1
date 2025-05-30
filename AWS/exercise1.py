import boto3
import random
import time



QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/118151820691/insult-filter-queue'


texts_with_insults = [
    "You are such a stupid idiot!",
    "I think you're a total moron.",
    "That person is clearly a groomer.",
    "What an air head, can't even spell right.",
    "This is a test message without any insults.",
    "Why don’t you just disappear, dumbass?",
    "She's not wrong, but he’s definitely a moron.",
    "I love working with smart people, unlike you.",
    "Let me know when you grow a brain, idiot.",
    "Nothing offensive here, I swear!"
]

def send_message_to_sqs(queue_url, message_body):
    """Send one message to SQS"""
    sqs = boto3.client('sqs', region_name='us-east-1')
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
        )
        print(f"Sent message: {message_body[:50]}... | ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending message: {e}")

def send_multiple_messages(queue_url, texts, count=10, delay=0.5):
    """Send multiple messages to SQS"""
    for i in range(count):
        text = random.choice(texts)
        send_message_to_sqs(queue_url, text)

if __name__ == "__main__":
    print("Sending test messages to SQS...")
    send_multiple_messages(QUEUE_URL, texts_with_insults, count=1000)
    print("Done sending messages.")