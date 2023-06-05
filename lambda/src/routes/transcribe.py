import os
import json
import uuid
import boto3

def transcribe_audio(bucket_name, audio_key, uuid):
    
    # Cria uma conexão com o serviço Amazon Transcribe
    transcribe = boto3.client('transcribe')
    
    # Define o formato do arquivo de entrada
    media_format = audio_key.split('.')[-1]
    
    # Configura a solicitação de transcrição
    transcribe_job = {
        'TranscriptionJobName': uuid,
        'LanguageCode': 'pt-BR',
        'MediaFormat': media_format,
        'Media': {
            'MediaFileUri': f's3://{bucket_name}/{audio_key}'
        },
        'OutputBucketName': bucket_name
    }
    
    # Inicia o trabalho de transcrição
    response = transcribe.start_transcription_job(**transcribe_job)
    
    
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=response['TranscriptionJob']['TranscriptionJobName'])
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        
    # Se a transcrição for concluída com sucesso, retorna o texto transcritor
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcribed_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcribed_text = boto3.client('s3').get_object(Bucket=bucket_name, Key=transcribed_uri.split('/')[-1])['Body'].read().decode('utf-8')
        return transcribed_text
    else:
        raise Exception('A transcrição falhou.')

def health(event, context):
    rdm = str(uuid.uuid4())
    a=transcribe_audio('trancrevendo-audio','speech_20230224000107430.mp3', rdm) # Nome do bucket, nome do arquivo de audio
    json_dict = json.loads(a)
    transcript = json_dict["results"]["transcripts"][0]["transcript"]
    return {
        'statusCode': 200,
        'body': transcript
    }