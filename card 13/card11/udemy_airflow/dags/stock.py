from airflow.decorators import dag, task  # Para definir DAGs e tarefas como funções
from airflow.hooks.base import BaseHook  # Para obter conexões configuradas no Airflow
from airflow.sensors.base import PokeReturnValue  # Para usar sensores no Airflow
from airflow.operators.python import PythonOperator  # Para tarefas que executam funções Python
from airflow.providers.docker.operators.docker import DockerOperator  # Para executar containers Docker
from airflow.providers.slack.notifications.slack_notifier import SlackNotifier  # Para notificações via Slack
from datetime import datetime  # Para trabalhar com datas
from astro import sql as aql  # Biblioteca Astro para manipulação de SQL no Airflow
from astro.files import File  # Gerenciamento de arquivos na Astro
from astro.sql.table import Table, Metadata  # Representação de tabelas no Airflow com Astro
from include.stock_market.tasks import (  # Importando funções específicas do projeto
    _get_stock_prices,
    _store_prices,
    _get_formatted_csv,
    bucket_name
)

# Variável com o símbolo da ação que será monitorada
SYMBOL = "AAPL"

# Definindo o DAG
@dag(
    start_date=datetime(2024, 11, 17),  # Data de início para a execução do DAG
    schedule_interval='@daily',  # Frequência: uma vez por dia
    catchup=False,  # Não executa execuções retroativas para dias anteriores à data de início
    tags=['stock'],  # Tag para identificar e categorizar o DAG
    on_success_callback=SlackNotifier(  # Notificação no Slack em caso de sucesso
        slack_conn_id='slack',  # Conexão configurada no Airflow para o Slack
        text='The DAG stock has succeeded',  # Mensagem de sucesso
        channel='general'  # Canal do Slack onde será enviada a notificação
    ),
    on_failure_callback=SlackNotifier(  # Notificação no Slack em caso de falha
        slack_conn_id='slack',
        text='The DAG stock has failed',
        channel='general'
    )
)
def stock():
    # Sensores monitoram eventos externos e retornam um valor para o DAG
    @task.sensor(poke_interval=30, timeout=300, mode='poke')  # Sensor configurado para verificar API
    def is_api_available() -> PokeReturnValue:
        """
        Verifica se a API de ações está disponível e retorna a URL da API.
        """
        api = BaseHook.get_connection('stock_api')  # Obtém os detalhes da conexão da API
        url = f"{api.host}{api.extra_dejson['endpoint']}"  # Constrói a URL da API com base na configuração

        response = requests.get(url, headers=api.extra_dejson['headers'])  # Faz a chamada à API
        condition = response.json().get('finance', {}).get('result') is not None  # Verifica se a resposta é válida

        # Retorna se a API está disponível e a URL para outras tarefas
        return PokeReturnValue(is_done=condition, xcom_value=url)

    # Tarefa para buscar os preços das ações usando a API
    get_stock_prices = PythonOperator(
        task_id='get_stock_prices',
        python_callable=_get_stock_prices,  # Função que faz a requisição de preços
        op_kwargs={
            'url': '{{ task_instance.xcom_pull(task_ids="is_api_available") }}',  # URL da API via XCom
            'symbol': SYMBOL  # Símbolo da ação
        },
    )

    # Tarefa para armazenar os preços das ações
    store_prices = PythonOperator(
        task_id='store_prices',
        python_callable=_store_prices,  # Função que armazena os dados obtidos
        op_kwargs={
            'stock': '{{ task_instance.xcom_pull(task_ids="get_stock_prices") }}',  # Dados via XCom
            'symbol': SYMBOL  # Símbolo da ação
        },
    )

    # Tarefa que formata os preços das ações utilizando um container Docker
    format_prices = DockerOperator(
        task_id='format_prices',
        image='airflow/stock-app',  # Nome da imagem Docker usada
        container_name='format_prices',  # Nome do contêiner gerado
        api_version='auto',  # Usa a versão da API detectada automaticamente
        auto_remove=True,  # Remove o contêiner após a execução
        docker_url="tcp://docker-proxy:2375",  # URL para o daemon Docker
        network_mode='container:spark-master',  # Modo de rede para o contêiner
        environment={  # Variáveis de ambiente passadas para o contêiner
            'SPARK_APPLICATION_ARGS': '{{ task_instance.xcom_pull(task_ids="store_prices") }}'
        },
        command='python /app/stock_transform.py',  # Comando executado no contêiner
        tty=True  # Habilita a alocação de terminal
    )

    # Tarefa para obter o caminho do CSV formatado
    get_formatted_csv = PythonOperator(
        task_id='get_formatted_csv',
        python_callable=_get_formatted_csv,  # Função que formata os dados e gera o CSV
        op_kwargs={
            'path': '{{ task_instance.xcom_pull(task_ids="store_prices") }}'  # Caminho do arquivo via XCom
        }
    )

    # Tarefa para carregar os dados formatados em um data warehouse (DW)
    load_to_dw = aql.load_file(
        task_id='load_to_dw',
        input_file=File(
            path=f's3://{bucket_name}/{{{{task_instance.xcom_pull(task_ids="get_formatted_csv")}}}}',  # Caminho do arquivo no S3
            conn_id='minio'  # Conexão configurada para acessar o bucket S3
        ),
        output_table=Table(  # Configuração da tabela de destino no DW
            name='stock_prices',  # Nome da tabela
            conn_id='postgres',  # Conexão com o banco de dados
            metadata=Metadata(schema='public')  # Esquema do banco de dados
        )
    )

    # Definindo a sequência de execução das tarefas
    is_api_available() >> get_stock_prices >> store_prices >> format_prices >> get_formatted_csv >> load_to_dw


# Instancia o DAG
stock()
