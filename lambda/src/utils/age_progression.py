import boto3
import json
import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def age_progression(target_age, image_key):
    try:
        s3 = boto3.client('s3')
        bucket_name = os.getenv('S3_BUCKET_NAME')

        # pega a imagem do bucket com base no image_key
        image_object = s3.get_object(Bucket=bucket_name, Key=image_key)
        image_content = image_object['Body'].read()
        image_content_b64 = base64.b64encode(image_content).decode('utf-8')

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

        # requisições para a api
        response = requests.post(url, headers=headers, json=data)
        
        if response.ok:
            try:
                prediction_id = response.json()["id"]
                print(prediction_id)
                prediction_url = f"{url}/{prediction_id}"
                while True:
                    response = requests.get(prediction_url, headers=headers)
                    if response.ok:
                        prediction_data = response.json()
                        if prediction_data["status"] == "succeeded":
                            # retorna a url da imagem gerada
                            return prediction_data["output"]
                        
            except Exception as e:
                print(e)
                print("Gateway Timeout")
                return {
                    'statusCode': 504,
                    'body': json.dumps(str(e))
                }  
        
    except Exception as e:
        print(e)
        print("Internal Server Error")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }  