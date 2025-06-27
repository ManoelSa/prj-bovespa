import boto3
import json
import urllib.parse

def lambda_handler(event, context):

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])
    print(f"Path do evento: s3://{bucket}/{key}")

    glue = boto3.client('glue')
    job_name = 'etl_bovespa'#'etl_bovespa_v2'

    try:
        response = glue.start_job_run(
            JobName=job_name,
            Arguments={
                '--s3_bucket': f's3://{bucket}/{key}'
            }
        )
        print(f"Job {job_name} iniciado com sucesso. Run ID: {response['JobRunId']}")
    except Exception as e:
        print(f"Erro ao iniciar o job {job_name}: {e}")
        raise e