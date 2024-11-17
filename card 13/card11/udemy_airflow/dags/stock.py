import requests
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook  # Nome correto é BaseHook
from airflow.sensors.base import PokeReturnValue
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.providers.docker.operators.docker import DockerOperator
from include.stock_maket.task import _get_stock_prices, _store_prices

SYMBOL = "AAPL"  # Exemplo de símbolo de ação


# Definindo o DAG com o decorador @dag
@dag(
    start_date=datetime(2024, 11, 17),  # Data de início do DAG
    schedule_interval='@daily',  # Executa uma vez por dia
    catchup=False,  # Não executa retroativamente
    tags=['stock'],  # Tag para categorizar o DAG
)
def stock():

    # Tarefa que atua como sensor para verificar se a API está disponível
    @task.sensor(poke_interval=30, timeout=600, mode='poke')
    def is_api_available() -> PokeReturnValue:
        # Obtém a conexão Airflow configurada no Admin > Connections
        api = BaseHook.get_connection('stock_api')

        # Monta a URL com base no host e no parâmetro 'endpoint' configurado no Extra
        url = f"{api.host}{api.extra_dejson['endpoint']}"

        # Faz a requisição GET para a API usando os headers configurados no Extra
        response = requests.get(url, headers=api.extra_dejson['headers'])

        # Verifica a condição para saber se a API está respondendo corretamente
        condition = response.json().get('finance', {}).get('result') is not None

        # Retorna o valor esperado pelo sensor
        return PokeReturnValue(is_done=condition, xcom_value=url)

    # Tarefa para obter os preços das ações
    get_stock_prices = PythonOperator(
        task_id='get_stock_prices',
        python_callable=_get_stock_prices,
        op_kwargs={'url': '{{ task_instance.xcom_pull(task_ids="is_api_available") }}', 'symbol': SYMBOL},
    )

    # Tarefa para armazenar os preços das ações
    store_prices = PythonOperator(
        task_id='store_prices',
        python_callable=_store_prices,
        op_kwargs={'stock': '{{ task_instance.xcom_pull(task_ids="get_stock_prices") }}', 'symbol': SYMBOL},
    )

    format_prices = DockerOperator(
        task_id='format_prices',
        image='airflow/stock-app',  # Nome da imagem Docker
        container_name='format_prices',  # Nome do contêiner
        api_version='auto',  # Versão da API Docker
        auto_remove=True,  # Remove o contêiner após execução
        docker_url="tcp://docker-proxy:2375",  # URL do daemon Docker
        network_mode='bridge',  # Modo de rede
        environment={  # Variáveis de ambiente
            'SPARK_APPLICATION_ARGS': '{{ task_instance.xcom_pull(task_ids="store_prices") }}'
        },
        command='python /app/stock_transform.py',  # Comando para rodar no contêiner
        tty=True  # Habilita o terminal
    )

    # Definindo as dependências entre as tarefas
    is_api_available() >> get_stock_prices >> store_prices >> format_prices


# Instancia o DAG
stock()
