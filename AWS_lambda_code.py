import json
import boto3

""" 

Code being run on AWS on lambda trigger (e.g. as images uploaded to bucket)

"""

def lambda_handler(event, context):
    rekognition_client = boto3.client("rekognition")
    msg = json.loads(event["Records"][0]["body"])["Records"][0]
    bucket, image_name = get_required_image_details(msg)
    image_labels = rekognition_client.detect_labels(Image={
        "S3Object" : {
            "Bucket" : bucket,
            "Name" : image_name
        }
    })
    
    labels_formatted = format_image_labels_for_store(image_labels["Labels"])
    store_labels_in_dynamo_db(image_name, labels_formatted)
    
    
def get_required_image_details(queue_image):
    # get image bucket
    bucket = queue_image["s3"]["bucket"]["name"]
    # get image name
    image_name = queue_image["s3"]["object"]["key"]
    
    return bucket, image_name

def format_image_labels_for_store(image_labels):
    # format labels to only the first 5 for storage
    labels_formatted = list()
    labels_extracted = 0
    labels_to_extract = 5
    
    if len(image_labels) < labels_to_extract:
        labels_to_extract = len(image_labels)
        
    while labels_extracted < labels_to_extract:
        labels_formatted.append(image_labels[labels_extracted]["Name"])
        labels_extracted += 1
        
    return labels_formatted
    
def store_labels_in_dynamo_db(image_name, labels_formatted):
    dynamo = boto3.resource("dynamodb", region_name="eu-west-1")

    images_table = dynamo.Table("cwktable")
    
    images_table.put_item(
       Item={
            "imagename": image_name,
            "labels" : labels_formatted
        }
    )