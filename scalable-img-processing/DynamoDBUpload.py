import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


table_name = 'studentdata'
table = dynamodb.Table(table_name)


def getItem():
    name='mr_bean'
    response = table.get_item(
        Key={
            'name' : name 
        }
    )

    print(response)
    details = response['Item']
    year = details['year']
    major = details['major']

    print("Person Name: ", name)
    print("Year: ", year)
    print("Major: ",major)

def upload():
    # read data from file
    with open('./student_data.json', 'r') as f:
        data = json.load(f)

    # insert data into table

    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(Item=item)

upload()
getItem()


