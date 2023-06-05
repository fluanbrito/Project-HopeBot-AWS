import os
import json
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ['TELEGRAM_BOT_TOKEN']

def telegram_send_messages(messages, chat_id):
    # envia mensagens para o telegram (resposta do bot)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    headers = {
        'Content-Type': 'application/json'
    }
    
    for message in messages:
        data = {
            'text': message,
            'chat_id': chat_id
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            print(f"Error sending message: {response.text}")

    return response
    
def telegram_send_image(image_url, chat_id):
    try:
        # baixa a imagem a partir da URL
        response = requests.get(image_url)

        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        data = {"chat_id": chat_id}
        files = {"photo": response.content}

        # enviar a imagem para o telegram (resposta do bot)
        response = requests.post(url, data=data, files=files)

        if response.status_code != 200:
            raise Exception(f"Erro ao enviar a imagem para o chat {chat_id}: {response.text}")

        return response.text

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

def get_uploaded_image(file_id, file_unique_id):
    s3 = boto3.client('s3')

    # requisição imagem pelo file_id
    response = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}")
    photo_path = response.json()['result']['file_path']

    # carrega a imagem
    photo_content = requests.get(f"https://api.telegram.org/file/bot{token}/{photo_path}").content
    image_format = photo_path.split(".")[-1]
    file_key = f"photos/{file_unique_id}.{image_format}"

    # salva no bucket
    s3.put_object(Bucket=os.environ['S3_BUCKET_NAME'], Key=file_key, Body=photo_content)

    url = s3.generate_presigned_url('get_object', Params={'Bucket': os.environ['S3_BUCKET_NAME'], 'Key': file_key}, ExpiresIn=3600)
    print(url)

    # path da imagem no bucket (preencher o slot da imagem)
    return file_key