import boto3
import pickle
import face_recognition
import pickle
import os 
import csv
import json

#input and output buckets
input_bucket = "546proj2inputbucket"
output_bucket = "546proj2outputbucket"

#initializing S3
s3client = boto3.resource('s3', region_name='us-east-1')
#intiliaze db
DBclient = boto3.resource('dynamodb', region_name='us-east-1')
table = DBclient.Table('studentdata')


#read ecoding information 
def encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data

def face_recognition_handler(event, context):
    #reading input from triggered event
    bucket = event['bucket_name']
    key = event['key']

    #storing the video at temp location
    local_path = '/tmp/'+key
    s3client.Bucket(bucket).download_file(key, local_path)

    #fetch encoding data
    encoding_data = encoding("encoding")

    #extracting frame from video 
    path = "/tmp/"
    os.system("ffmpeg -i " + str(local_path) + " -r 1 " + str(path) + "image-%3d.jpeg")

    #extract face from the frame and encode the data
    print("Extracting frames from video...")
    extracted_image = face_recognition.load_image_file("/tmp/image-001.jpeg")
    extracted_face_encoding = face_recognition.face_encodings(extracted_image)[0]

    #comapre faces in video with encoding data
    print("Comparing faces...")
    index = 0
    for known_face_encoding in encoding_data['encoding']:
        results = face_recognition.compare_faces([known_face_encoding], extracted_face_encoding)
        if results[0] == True:
            break
        else:
            index = index + 1

    
    #fetching student information from dynamoDB
    name = encoding_data['name'][index]
    print("Face recognized successfully.. ")
    print("Name: ", name)
    print("Fetching student information...")
    response = table.get_item(
        Key={
            'name' : name 
        }
    )

    details = response['Item']
    year = details['year']
    major = details['major']

    #storing output in a csv file
    split_name = key.split('.',1)[0]
    csv_file_name = split_name + '.csv'

    #printing output
    print("File name: ", key)
    print("Person Name: ", name)
    print("Year: ", year)
    print("Major: ",major)

    #saving results to outpt bucket 
    with open('/tmp/'+csv_file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([key, name, major, year])

    s3client.Bucket(output_bucket).upload_file('/tmp/'+csv_file_name, csv_file_name)
    print('"Uploaded {0} to {1} bucket successfully!!"'.format(csv_file_name, output_bucket))
    return {
        'statusCode': 200,
        'body': json.dumps({
            'res': [key, name, major, year]
        })
    }
