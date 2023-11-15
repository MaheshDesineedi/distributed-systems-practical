import boto3
import json
import time

session = boto3.Session(profile_name='default')

input_bucket='546proj2inputbucket'
output_bucket='546proj2outputbucket'

s3 = session.resource('s3')
ip_bucket = s3.Bucket(input_bucket)
op_bucket = s3.Bucket(output_bucket)

lambdaClient = session.client("lambda")
functionARN = 'arn:aws:lambda:us-east-1:025818375297:function:FaceRecognition'

def sleep(seconds):
    print("Sleeping for {0} seconds...".format(seconds))
    time.sleep(seconds)

def printS3Output(fileNames):
    for file in fileNames:
        res = op_bucket.meta.client.get_object(Bucket=output_bucket, Key=file)
        val = res['Body'].read().decode("utf-8")
        print("[Output]: {0}".format(val))

def invokeLambda(process_keys):
    if not process_keys:
        return
    
    for key in process_keys:

        event = {
            "bucket_name": input_bucket,
            "key": key
        }

        response = lambdaClient.invoke(
            FunctionName=functionARN,
            InvocationType='Event',
            LogType='None',
            Payload=json.dumps(event)
        )

        print("Sent request to lambda for {0} [status: {1}]".format(key, response['StatusCode']))

def main():
    processed_ip_keys = {}
    processed_op_keys = {}

    check_ip = 3; check_op = 3
    while(check_ip > 0 or check_op > 0):
        sleep(2)

        process_ip = []

        for obj in ip_bucket.objects.all():
            if not obj.key in processed_ip_keys:
                process_ip.append(obj.key)
                processed_ip_keys[obj.key] = 1

        if not process_ip:
            sleep(2)
            check_ip = check_ip - 1
            # continue
        else:
            check_in = 3
            invokeLambda(process_ip)
            process_ip = [] # clear

        process_op = []
        
        for obj in op_bucket.objects.all():
            if not obj.key in processed_op_keys:
                process_op.append(obj.key)
                processed_op_keys[obj.key] = 1

        if not process_op:
            sleep(2)
            check_op = check_op - 1
            # continue
        else:
            check_op = 3
            printS3Output(process_op)
            process_op = [] # clear

main()

    






