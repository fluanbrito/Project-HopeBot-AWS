import boto3
import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def age_progression(event, context):
    s3 = boto3.client('s3')

    file_name = event['file_name']
    target_age = event['target_age']
    bucket_name = os.getenv('S3_BUCKET_NAME')
    image_key = 'age_progression/' + file_name;

    image_object = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_content = image_object['Body'].read()
    image_content_b64 = base64.b64encode(image_content).decode('utf-8')
    
    print(image_content_b64)

    url = os.getenv('API_URL')
    headers = {
        "Authorization": f"Token {os.getenv('API_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {
        "version": "9222a21c181b707209ef12b5e0d7e94c994b58f01c7b2fec075d2e892362f13c",
        "input": {
            "image": f"data:image/jpeg;base64,{image_content_b64}",
            "target_age": target_age
        },
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.ok:
        prediction_id = response.json()["id"]
        print(prediction_id)
        prediction_url = f"{url}/{prediction_id}"
        while True:
            response = requests.get(prediction_url, headers=headers)
            if response.ok:
                prediction_data = response.json()
                if prediction_data["status"] == "succeeded":
                    return {
                        "statusCode": 200,
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": prediction_data["output"]
                    }
            else:
                return {
                    "statusCode": 504,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": { "message": "Gateway Timeout" }
                }
    else:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": { "message": "Internal Server Error" }
        }