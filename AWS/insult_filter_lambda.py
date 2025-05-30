


def lambda_handler(event, context):
    insults = ['dumb', 'moron', 'stupid', 'idiot', 'groomer', 'acrotomophile', 'air head', 'accident']

    for record in event['Records']:
        body = record['body']
        for insult in insults:
            body = body.replace(insult, 'CENSORED')
        print("Filtered:", body)

    return {'statusCode': 200, 'body': 'Messages processed'}