import os
import boto3
from datetime import datetime, time

print('Loading function')

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

def return_state(glue, runId, gluejobname):
    status = glue.get_job_run(JobName=gluejobname, RunId=runId['JobRunId'])
    state = status['JobRun']['JobRunState']

    return state


def lambda_handler(event, context):
    # Get the object from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    base_key = os.path.splitext(os.path.basename(object_key))[0]
    
    # Check if the uploaded file is a CSV
    if not object_key.endswith('.csv'):
        print(f"Object {object_key} is not a CSV file.")
        return
    
    # Get the file from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    contents = response['Body'].read().decode('utf-8')
    
    ## scripts % zip glue_trigger.zip glue_trigger.py
    # Process the file
    glue = boto3.client('glue')
    # gluejobname = "test-job"
    gluejobname = f"{base_key.lower()}_load"


    try:
        # runId = glue.start_job_run(JobName=gluejobname)

        print("Started Glue job")
        state = "RUNNING"

        # Start the Glue job
        response = glue.start_job_run(JobName=gluejobname)

        # Wait for the job to complete
        job_run_id = response['JobRunId']
        # job_run = glue.get_job_run(JobName=gluejobname, RunId=job_run_id)

        destination_bucket = 'byte-barista-data-output-bucket'
        destination_key = f"processed_{base_key}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': bucket_name, 'Key': object_key}, Key=destination_key)

        if return_state(glue, response, gluejobname) == 'SUCCEEDED':
            s3.delete_object(Bucket=bucket_name, Key=object_key)


        # while True:
        #     response = glue.get_job_run(JobName=gluejobname, RunId=job_run_id)
        #     status = response['JobRun']['JobRunState']

        #     if status == 'SUCCEEDED':
        #         # Move the processed file to another bucket
        #         destination_bucket = 'byte-barista-data-output-bucket'
        #         destination_key = f"processed_{base_key}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        #         s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': bucket_name, 'Key': object_key}, Key=destination_key)
        #         break

        #     elif status == 'FAILED':
        #         raise Exception('Glue job failed')

        #     time.sleep(10)

        # Delete the S3 object
        # s3.delete_object(Bucket=bucket_name, Key=object_key)

        # while job_run['JobRun']['JobRunState'] not in ['SUCCEEDED', 'FAILED', 'STOPPED']:
        #     job_run = glue.get_job_run(JobName=gluejobname, RunId=job_run_id)

        # if job_run['JobRun']['JobRunState'] == 'SUCCEEDED':
        #     # The job succeeded, so you can execute subsequent functions here
        #     print('The Glue job succeeded')
        #     # Move the processed file to another bucket
        #     destination_bucket = 'byte-barista-data-output-bucket'
        #     destination_key = f"processed_{base_key}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"

        #     s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': bucket_name, 'Key': object_key}, Key=destination_key)

        #     # s3_resource.Object(destination_bucket, destination_key).put(Body=contents)
            
        #     # Delete the original file
        #     s3.delete_object(Bucket=bucket_name, Key=object_key)

        # while state not in ['SUCCEEDED', 'FAILED', 'STOPPED']:
        #     state = return_state(glue, runId, gluejobname)
        #     time.sleep(10)

        # if state == 'SUCCEEDED':
        #     # Move the processed file to another bucket
        #     destination_bucket = 'byte-barista-data-output-bucket'
        #     destination_key = f"processed_{base_key}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"

        #     s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': bucket_name, 'Key': object_key}, Key=destination_key)

        #     # s3_resource.Object(destination_bucket, destination_key).put(Body=contents)
            
        #     # Delete the original file
        #     s3.delete_object(Bucket=bucket_name, Key=object_key)

    except Exception as e:
        print(e)
        raise
    
    return {
        'statusCode': 200,
        'body': 'File processed and moved to processed-bucket'
    }
