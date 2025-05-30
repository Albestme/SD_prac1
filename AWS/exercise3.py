import lithops

lithops.config.CHECK_ARGUMENTS = False

config = {
    'lithops': {
        'mode': 'serverless',
        'compute_backend': 'aws_lambda',
        'storage_backend': 'aws_s3',
        'memory': 2048,
        'timeout': 300,
        'runtime': 'lithops-hello-default'
    },
    'aws_lambda': {
        'region': 'us-east-1'
    }
}

import boto3
import os


def filter_insults_s3(data):
    s3 = boto3.client('s3', region_name='us-east-1')

    bucket = data['bucket']
    key = data['key']

    # Download file directly into memory
    response = s3.get_object(Bucket=bucket, Key=key)
    text = response['Body'].read().decode('utf-8')

    insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']
    censored_count = 0
    for insult in insults:
        count = text.count(insult)
        censored_count += count
        text = text.replace(insult, "CENSORED")

    # Upload filtered text back to S3 from memory
    output_key = f"output/{os.path.basename(key)}"
    s3.put_object(Body=text.encode('utf-8'), Bucket=bucket, Key=output_key)

    return censored_count

def reduce_censored_counts(results):
    total = sum(results)
    print(f"Total censored insults: {total}")
    return total


def main():
    BUCKET = 'exercise3.12341890234712'
    PREFIX = 'input/'  # Folder with input .txt files

    # List all files in the input folder
    s3 = boto3.client('s3', region_name='us-east-1')
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
    files = [{'data': {'bucket': BUCKET, 'key': item['Key']}} for item in response.get('Contents', [])]

    if not files:
        print("No files found in input folder.")
        return

    # Run Lithops map
    fexec = lithops.FunctionExecutor()
    fexec.map(filter_insults_s3, files)

    # Reduce step: collect results and count total insults
    results = fexec.get_result()
    total_insults = reduce_censored_counts(results)

    print(f"All files processed. Total insults censored: {total_insults}")


if __name__ == "__main__":
    main()
