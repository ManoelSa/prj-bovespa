import json
import requests
import base64
import pandas as pd
import boto3
from io import BytesIO
import datetime
import pyarrow as pa
import pyarrow.parquet as pq

#Variaveis
current = datetime.datetime.now()
dt_ref = current.strftime('%Y-%m-%d')
dataproc = dt_ref.replace('-','')

def bovespa()-> pd.DataFrame:
    payload = {'language': 'pt-br', 
               'pageNumber': 1, 
               'pageSize': 200, 
               'index': 'IBOV', 
               'segment': '2'}

    encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
    url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{encoded_payload}"
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
                "Referer": "https://sistemaswebb3-listados.b3.com.br/"}

    response = requests.get(url, headers=headers)
    data = response.json()

    df = pd.DataFrame(data['results'])
    df['dt_ref'] = dt_ref

    return df

def lambda_handler(event, context):
    df_bovespa = bovespa()
    table = pa.Table.from_pandas(df_bovespa)
    buffer = BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)

    s3 = boto3.client('s3')

    bucket_name = 'bck-bovespa'
    object_key = f"raw/dataproc={dataproc}/bovespa_{dataproc}.parquet"

    s3.upload_fileobj(buffer, bucket_name, object_key)
    print("Parquet enviado com sucesso para o S3!")

    return {
            'statusCode': 200,
            'body': json.dumps(f'Arquivos Bovespa do dia {dt_ref} foram carregados no bucket: {bucket_name}')
            }