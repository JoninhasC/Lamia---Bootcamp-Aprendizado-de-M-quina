from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.sensors.base import PokeReturnValue
from airflow.providers.docker.operators.docker import DockerOperator
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from include.stock_market.tasks import _get_stock_prices, _store_prices, _get_formatted_csv, BUCKET_NAME
import requests
from datetime import datetime

# Variáveis globais
BUCKET_NAME = 'stockmarket2024'
SYMBOL = "AAPL"

@dag(
    start_date=datetime(2024, 11, 17),
    schedule_interval='@daily',
    catchup=False,
    tags=['stock_market']
)
def stock_market():
    # Sensor para verificar se a API está disponível
    @task.sensor(poke_interval=30, timeout=300, mode='poke')
    def is_api_available() -> PokeReturnValue:
        api = BaseHook.get_connection('stock_api')
        url = f"{api.host}{api.extra_dejson['endpoint']}"
        response = requests.get(url, headers=api.extra_dejson['headers'])
        condition = response.json()['finance']['result'] is None
        return PokeReturnValue(is_done=condition, xcom_value=url)

    # Tarefa para obter os preços das ações
    get_stock_prices = PythonOperator(
        task_id='get_stock_prices',
        python_callable=_get_stock_prices,
        op_kwargs={'url': '{{ task_instance.xcom_pull(task_ids="is_api_available") }}', 'symbol': SYMBOL}
    )

    # Tarefa para armazenar os preços das ações
    store_prices = PythonOperator(
        task_id='store_prices',
        python_callable=_store_prices,
        op_kwargs={
            'stock': '{{ task_instance.xcom_pull(task_ids="get_stock_prices") }}',
            'symbol': SYMBOL
        },
    )

    # Tarefa para formatar os preços usando um container Docker
    format_prices = DockerOperator(
        task_id='format_prices',
        max_active_tis_per_dag=1,
        image='airflow/spark-app',
        container_name='trigger_job',
        environment={
            'SPARK_APPLICATION_ARGS': '{{ ti.xcom_pull(task_ids="store_prices") }}'
        },
        api_version='auto',
        auto_remove=True,
        docker_url='tcp://docker-proxy:2375',
        network_mode='container:spark-master',
        tty=True,
        xcom_all=False,
        mount_tmp_dir=False
    )

    # Tarefa para obter o caminho do arquivo formatado no S3
    get_formatted_csv = PythonOperator(
        task_id='get_formatted_csv',
        python_callable=_get_formatted_csv,
        op_kwargs={'location': '{{ ti.xcom_pull(task_ids="store_prices") }}'},
    )

    # Tarefa para carregar os dados formatados no data warehouse
    load_to_dw = aql.load_file(
        task_id='load_to_dw',
        input_file=File(
            # Utiliza o caminho retornado pela tarefa anterior
            path='{{ task_instance.xcom_pull(task_ids="get_formatted_csv") }}',
            conn_id='minio'
        ),
        output_table=Table(
            name='stock',
            conn_id='postgres',
            metadata=Metadata(schema='public')
        )
    )

    # Fluxo de execução do DAG
    is_api_available() >> get_stock_prices >> store_prices >> format_prices >> get_formatted_csv >> load_to_dw

stock_market()
