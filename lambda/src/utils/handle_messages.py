from services.lex import lex_send_message
from services.telegram import telegram_send_image, telegram_send_messages

def handle_messages(message, session_id, chat_id):
    # envia a mensagem do usuário para o lex
    lex_response = lex_send_message(message, session_id)
    print(lex_response)
    print('lex_response/text')
    intent = lex_response['sessionState']['intent']
    session_attributes = lex_response['sessionState']['sessionAttributes']

    # se a intent for confirmada (slots preenchidos) e AgeProgressionImage existir
    if 'confirmationState' in intent and intent['confirmationState'] == 'Confirmed':
        if 'AgeProgressionImage' in session_attributes:
            image_url = session_attributes['AgeProgressionImage']
            # envia a imagem para o telegram
            response = telegram_send_image(image_url, chat_id)
            print(response.text)
            print('telegram_send_image response/text')

    # se tiver as mensagens no retorno do lex (resposta do bot)
    if 'messages' in lex_response:
        messages = [message['content'] for message in lex_response['messages'] if message['contentType'] == 'PlainText']
        if messages:
            # envia as mensagens pro telegram (resposta do bot)
            response = telegram_send_messages(messages, chat_id)
            print(response.text)
            print('telegram send messages/text')
            return {
                'statusCode': response.status_code,
                'body': response.text
            }