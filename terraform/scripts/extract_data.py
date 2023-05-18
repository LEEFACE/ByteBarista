import boto3
import csv

def lambda_handler(event, context):
    # Get the S3 object from the event
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Read the CSV file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    rows = response['Body'].read().decode('utf-8').split('\n')

    # Extract the data from the CSV file
    data = []
    for row in csv.reader(rows):
        data.append(row)

    # Do something with the data
    print(data)
