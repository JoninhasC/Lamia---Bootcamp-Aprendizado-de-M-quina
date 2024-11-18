from io import BytesIO
from airflow.hooks.base import BaseHook
import json
import requests
from minio import Minio
BUCKET_NAME= 'stockmarket2024'  # Certifique-se de que o nome do bucket é válido
def _get_minio_client():
    minio = BaseHook.get_connection('minio')
    client = Minio(
        endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],
        access_key=minio.login,
        secret_key=minio.password,
        secure=False
    )
    return client

# Função para buscar os preços das ações
def _get_stock_prices(url, symbol):
    try:
        url = f"{url}{symbol}?metrics=high&interval=1d&range=1y"
        api = BaseHook.get_connection('stock_api')
        response = requests.get(url, headers=api.extra_dejson['headers'])
        response.raise_for_status()

        data = response.json()
        if 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
            return json.dumps(data['chart']['result'][0])
        else:
            print(f"Dados inesperados para {symbol}: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados para {symbol}: {e}")
        return None


def _store_prices(stock):
    client = _get_minio_client()


    try:
        # Verifique se o bucket existe, se não, cria
        if not client.bucket_exists(BUCKET_NAME):
            print(f"Bucket '{BUCKET_NAME}' não encontrado, criando agora.")
            client.make_bucket(BUCKET_NAME)
        else:
            print(f"Bucket '{BUCKET_NAME}' já existe.")

        stock = json.loads(stock)
        if 'meta' not in stock or 'symbol' not in stock['meta']:
            print("Dados do estoque não estão completos, faltando 'meta' ou 'symbol'.")
            return None

        symbol = stock['meta']['symbol']
        data = json.dumps(stock, ensure_ascii=False).encode('utf-8')

        # Tente armazenar no MinIO
        objw = client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=f'{symbol}/prices.json',
            data=BytesIO(data),
            length=len(data)
        )
        print(f"Dados armazenados com sucesso em {objw.bucket_name}/{symbol}/prices.json")
        return f'{objw.bucket_name}/{symbol}'
    except Exception as e:
        print(f"Erro ao armazenar dados no MinIO: {e}")
        return None

def _get_formatted_csv():
    client = _get_minio_client()
    objects = client.list_objects(BUCKET_NAME, prefix='AAPL/formatted_prices/', recursive=True)
    csv_file = [obj for obj in objects if obj.object_name.endswith('.csv')][0]
    return f's3://{csv_file.bucket_name}/{csv_file.object_name}'
