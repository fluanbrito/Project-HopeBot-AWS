import boto3
import os
import urllib

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

source_bucket_name = 'compare-faces-sprint-10-11'
target_bucket_name = 'pessoas-desaparecidas-sprint-10-11'

def compare_faces(event, context):
    # Obter a lista de objetos no bucket de origem
    response = s3.list_objects_v2(Bucket=source_bucket_name)
    source_objects = response['Contents']
    
    # Obter o objeto mais recente do bucket de origem
    source_object = max(source_objects, key=lambda obj: obj['LastModified'])
    source_image_key = source_object['Key']
    source_image_url = f"https://{source_bucket_name}.s3.amazonaws.com/{urllib.parse.quote_plus(source_image_key)}"
    source_image_object = s3.get_object(Bucket=source_bucket_name, Key=source_image_key)
    source_image_content = source_image_object['Body'].read()
    
    # Comparar a nova imagem com as imagens no bucket alvo
    target_image_results = []
    target_objects = s3.list_objects_v2(Bucket=target_bucket_name)['Contents']
    for target_object in target_objects:
        target_image_key = target_object['Key']
        if target_image_key == source_image_key:
            continue
        
        target_image_url = f"https://{target_bucket_name}.s3.amazonaws.com/{urllib.parse.quote_plus(target_image_key)}"
        target_image_object = s3.get_object(Bucket=target_bucket_name, Key=target_image_key)
        target_image_content = target_image_object['Body'].read()
        
        # Comparar as imagens usando o Amazon Rekognition
        response = rekognition.compare_faces(
            SourceImage={
                'Bytes': source_image_content
            },
            TargetImage={
                'Bytes': target_image_content
            },
        )
        
        # Capturar a similaridade do rosto correspondente, se houver
        if response['FaceMatches']:
            similarity = response['FaceMatches'][0]['Similarity']
            target_image_results.append({
                'imagem_correspondente': target_image_url,
                'similaridade': similarity
            })
        else:
            print('Nenhum rosto correspondente encontrado.')

    if target_image_results:
        return {
            'statusCode': 200,
            'body': {
                'Imagem enviada para comparação:': source_image_url,
                'Correspondência': target_image_results
            }
        }
    else:
        return {
            'statusCode': 200,
            'body': 'Nenhuma correspondência encontrada.'
        }
