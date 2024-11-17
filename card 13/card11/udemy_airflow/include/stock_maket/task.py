from airflow.hooks.base import BaseHook  # Para obter conexões configuradas no Airflow
import requests  # Para fazer chamadas HTTP
from airflow.exceptions import AirflowNotFoundException  # Exceção personalizada para Airflow
import json  # Para manipulação de dados em JSON
from minio import Minio  # Biblioteca para interação com o MinIO
from io import BytesIO  # Para manipulação de fluxos de dados binários em memória

# Nome do bucket no MinIO onde os dados serão armazenados
BUCKET_NAME = 'stock_market'

# Função para criar e retornar um cliente do MinIO
def __get_minio_client():
    """
    Obtém uma instância do cliente MinIO configurada com base nos detalhes de conexão do Airflow.
    """
    minio = BaseHook.get_connection('minio')  # Conexão MinIO configurada no Airflow
    client = Minio(
        endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],  # Extrai o host do URL da conexão
        access_key=minio.login,  # Chave de acesso do MinIO
        secret_key=minio.password,  # Chave secreta do MinIO
        secure=False  # Configuração para conexões HTTP (não seguras)
    )
    return client  # Retorna o cliente MinIO configurado

# Função para buscar os preços das ações
def _get_stock_prices(url, symbol):
    """
    Faz uma requisição à API de ações e retorna os dados formatados em JSON.
    """
    # Constrói a URL com os parâmetros do símbolo, intervalo e período
    url = f"{url}{symbol}?metrics=high&interval=1d&range=1y"
    api = BaseHook.get_connection('stock_api')  # Conexão com a API configurada no Airflow

    # Faz a chamada GET à API
    response = requests.get(url, headers=api.extra_dejson['headers'])

    # Retorna os resultados no formato JSON como string
    return json.dumps(response.json()['chart']['result'][0])

# Função para armazenar os preços no MinIO
def _store_prices(stock):
    """
    Armazena os preços das ações em um bucket MinIO.
    """
    client = __get_minio_client()  # Obtém o cliente MinIO
    bucket_name = 'stock_market'  # Nome do bucket

    # Verifica se o bucket existe; se não existir, ele será criado
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(bucket_name)

    # Converte os dados de string JSON para dicionário
    stock = json.loads(stock)

    # Obtém o símbolo das ações a partir dos dados
    symbol = stock['meta']['symbol']

    # Converte os dados para bytes e codifica em UTF-8
    data = json.dumps(stock, ensure_ascii=False).encode('utf8')

    # Armazena os dados como um objeto no MinIO
    objw = client.put_object(
        bucket_name=BUCKET_NAME,  # Nome do bucket onde o objeto será armazenado
        object_name=f'{symbol}/prices.json',  # Nome do objeto no bucket
        data=BytesIO(data),  # Dados a serem armazenados
        length=len(data)  # Tamanho dos dados em bytes
    )

    # Retorna o caminho do objeto armazenado
    return f'{objw.bucket_name}/{symbol}'

# Função para obter o caminho de um arquivo CSV formatado
def _get_formatted_csv(path):
    """
    Busca um arquivo CSV formatado no bucket MinIO com base no prefixo especificado.
    """
    path = 'stock-market/APPL'  # Exemplo de caminho do bucket/objeto
    client = __get_minio_client()  # Obtém o cliente MinIO

    # Prefixo utilizado para localizar objetos dentro do bucket
    prefix_name = f"{path.split('/')[1]}/formatted_prices/"

    # Lista objetos no bucket com o prefixo especificado
    objects = client.list_objects(BUCKET_NAME, prefix=prefix_name, recursive=True)

    # Itera pelos objetos encontrados para localizar o arquivo CSV
    for obj in objects:
        if obj.object_name.endswith('.csv'):  # Verifica se o nome do objeto termina com '.csv'
            return obj.object_name  # Retorna o nome do objeto encontrado

    # Lança uma exceção caso nenhum arquivo CSV seja encontrado
    raise AirflowNotFoundException('The csv file does not exist')
