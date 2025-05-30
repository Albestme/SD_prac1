import lithops
import boto3

def lambda_wrapper(text):
    return filter_insults({'body': text}, None)

def filter_insults(event, context):
    text = event.get('body', '')
    insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
    for insult in insults:
        text = text.replace(insult, 'CENSORED')
    return {'filtered_text': text}

def poll_sqs_messages(queue_url, max_messages=10, visibility_timeout=30, wait_time=20):
    sqs = boto3.client('sqs', region_name='us-east-1')
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time,
            VisibilityTimeout=visibility_timeout,
            MessageAttributeNames=['All']
        )
        return response.get('Messages', [])
    except Exception as e:
        print(f"Error polling SQS: {e}")
        return []

def delete_sqs_message(queue_url, receipt_handle):
    sqs = boto3.client('sqs', region_name='us-east-1')
    try:
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print("Message deleted.")
    except Exception as e:
        print(f"Error deleting message: {e}")

def stream_operation(function, maxfunc, queue_url):
    """
    function: Python function to apply to each message (e.g., filter_insults)
    maxfunc: Maximum number of concurrent Lithops workers (Lambda functions)
    queue_url: URL of the SQS queue to pull messages from
    """

    while True:
        # Step 1: Poll the queue for up to maxfunc messages
        messages = poll_sqs_messages(queue_url, max_messages=maxfunc)
        if not messages:
            print("No more messages in queue.")
            break

        # Step 2: Extract message bodies and receipt handles
        message_bodies = [msg['Body'] for msg in messages]
        receipt_handles = [msg['ReceiptHandle'] for msg in messages]

        # Step 3: Process messages in parallel using Lithops
        fexec = lithops.FunctionExecutor(workers=maxfunc)
        fexec.map(function, message_bodies)
        results = fexec.get_result()

        # Step 4: Print filtered output (or store it)
        for result in results:
            print(f"Filtered text: {result}")

        # Step 5: Delete all successfully processed messages
        for handle in receipt_handles:
            delete_sqs_message(queue_url, handle)


if __name__ == "__main__":
    texts = ["You're so stupid!", "I'm not dumb.", "You moron!"]

    stream_operation(lambda_wrapper, 5,
    'https://sqs.us-east-1.amazonaws.com/118151820691/exercise2_queue')