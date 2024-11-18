# Importando as bibliotecas necessárias do Airflow
from airflow.decorators import dag, task  # Importa os decoradores 'dag' e 'task' para criação do fluxo de trabalho e tarefas.
from airflow import DAG  # Importa a classe DAG do Airflow para definir um DAG explicitamente (não usado diretamente no código, mas pode ser útil em DAGs maiores).
from airflow.operators.python import PythonOperator  # Importa o PythonOperator, usado para executar funções Python dentro do DAG.
from datetime import datetime  # Importa o módulo datetime para definir a data de início do DAG.

# Função para a tarefa definida com PythonOperator
def _task_e(ti):
    print("Task E")  # Imprime no log "Task E" quando a tarefa for executada.
    return 42  # Retorna o valor 42, que será acessado por outras tarefas através do XCom.

# Definindo o DAG com o decorador @dag
@dag(
    start_date=datetime(2024, 11, 17),  # Define a data de início da execução do DAG. O DAG começará a rodar em 17 de novembro de 2024.
    schedule_interval='@daily',  # Define que o DAG será executado uma vez por dia.
    catchup=False,  # Impede que o Airflow execute tarefas retroativas. Ou seja, tarefas de datas passadas não serão executadas ao ativar o DAG.
    tags=['taskExemplo02'],  # Atribui uma tag ao DAG, útil para filtragem e organização no Airflow UI.
)
def taskflow_x():

    # Tarefa definida com o PythonOperator
    task_e_operator = PythonOperator(
        task_id='task_e',  # Define o ID da tarefa no DAG.
        python_callable=_task_e,  # Especifica a função Python que será executada quando a tarefa for chamada.
    )

    # Tarefa definida com o decorador @task
    @task
    def task_f(value):  # Função decorada com @task, que será executada dentro do fluxo do DAG.
        print("Task F")  # Imprime "Task F" no log.
        print(f"Valor recebido de task_e: {value}")  # Imprime o valor que foi passado para 'task_f', que vem de 'task_e'.

    # Chama task_f e passa o valor retornado por task_e através do XCom
    task_f(task_e_operator.output)  # Passa o valor de 'task_e' para 'task_f'. O valor de 'task_e_operator.output' será o valor retornado pela função _task_e, que é 42.

# Chamando a função 'taskflow_x' para criar a DAG
taskflow_x()  # Invoca a função decorada para criar o DAG e executar as tarefas.
