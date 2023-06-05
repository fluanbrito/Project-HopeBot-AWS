import os
import json
import boto3
from utils.age_progression import age_progression
from dotenv import load_dotenv

load_dotenv()

lex_bot_id = os.environ['LEX_BOT_ID']
lex_bot_alias_id = os.environ['LEX_BOT_ALIAS_ID']
lex_bot_name = os.environ['LEX_BOT_NAME']
lex_bot_alias = os.environ['LEX_BOT_ALIAS']
lex_bot_region = os.environ['AWS_REGION']
lex_client = boto3.client('lexv2-runtime', region_name=lex_bot_region)

def handle_lex_event(event, context):
    session_state = event['sessionState']
    intent_name = session_state['intent']['name']
    state = session_state['intent']['state']
    target_age = session_state['intent']['slots']['TargetAge']
    image_url = session_state['intent']['slots']['ImageURL']

    if target_age is None:
        # retira o TargetAge se ainda não houver valor
        session_state['intent']['slots'].pop('TargetAge', None)

    if 'proposedNextState' in event:
        # constroi o dialogAction com base no proposedNextState, se existir
        dialog_action = event['proposedNextState']['dialogAction']
        dialog_action_type = dialog_action['type']
        slot_to_elicit = dialog_action['slotToElicit']
    else:
        # dialogAction padrão
        dialog_action_type = 'Delegate'
        slot_to_elicit = None

    dialog_action_response = {
        'type': dialog_action_type
    }

    if slot_to_elicit:
        dialog_action_response['slotToElicit'] = slot_to_elicit
    if intent_name:
        dialog_action_response['intent'] = {'name': intent_name}
    if dialog_action_type == 'Delegate':
        dialog_action_response['state'] = state

    session_state['dialogAction'] = dialog_action_response

    response = {
        "sessionState": session_state,
    }

    if target_age is not None and 'value' in target_age and 'value' in image_url:
        target_age_value = target_age['value']['interpretedValue']
        image_key_value = image_url['value']['interpretedValue']

        # se os slots estiverem preenchidos faz a requisição p/ API
        processed_image = age_progression(target_age_value, image_key_value)
        print(processed_image)
        print('processed_image')

        # adiciona AgeProgressionImage com a url da nova imagem no sessionAttributes
        response['sessionState']['sessionAttributes']['AgeProgressionImage'] = processed_image
        response['sessionState']['intent']['confirmationState'] = 'Confirmed'

    print(response)
    print("handle_lex_event response")
    return response

def lex_send_message(message, session_id):
    print(f"message: {message}; message type: {type(message)}")

    try:
        # envia as mensagens do usuário para o lex
        response = lex_client.recognize_text(
            botId=lex_bot_id,
            botAliasId=lex_bot_alias_id,
            localeId='pt_BR',
            sessionId=session_id,
            text=message,
        )

        print(response)
        print('recognize_text response/lex event')
        return response
    
    except Exception as e:
        print(e)
        print("lex_send_message/lex event")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }        