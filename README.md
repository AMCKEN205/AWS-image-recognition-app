# AWS-image-recognition-app
simple app using AWS' rekognition service.

Images are uploaded to an AWS bucket, the details of the image are then logged in an SQS queue which triggers a lambda function used to perform image object recognition. Image details along with identified image object names are stored in a dynamoDB table. 
