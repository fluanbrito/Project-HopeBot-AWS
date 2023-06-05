import os
import telegram
import boto3
import json
from services.telegram import get_uploaded_image
from services.lex import handle_lex_event
from utils.session_id import generate_id
from utils.handle_messages import handle_messages
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.environ['TELEGRAM_BOT_TOKEN']
bot = telegram.Bot(token=telegram_token)
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    print(event)
    try:
        # telegram event
        if 'body' in event:
            body = json.loads(event['body'])
            chat_id = str(body['message']['chat']['id'])
            session_id = generate_id(chat_id)

            if 'message' in body and 'text' in body['message']:
                message = body['message']['text']
                return handle_messages(message, session_id, chat_id)
                        
            if 'message' in body and 'photo' in body['message']:
                file_id = body['message']['photo'][-1]['file_id']
                file_unique_id = body['message']['photo'][-1]['file_unique_id']
                file_key = get_uploaded_image(file_id, file_unique_id)
                return handle_messages(file_key, session_id, chat_id)

        # lex event
        if 'sessionId' in event and 'sessionState' in event:
            return handle_lex_event(event, context)

    except Exception as e:
        print(e)
        print('first exception')
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }