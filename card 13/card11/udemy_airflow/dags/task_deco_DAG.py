# Importando as bibliotecas necessárias do Airflow
from airflow.decorators import dag, task
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Função para a tarefa definida com PythonOperator
def _task_e(ti):
    print("Task E")
    return 42  # Retorna o valor 42 que pode ser acessado por outras tarefas

# Definindo a DAG com o decorador @dag
@dag(
    start_date=datetime(2024, 12, 1),  # Data de início da DAG
    schedule_interval='@daily',  # Agendamento da DAG (executa uma vez por dia)
    catchup=False,  # Não executar tarefas retroativas
    tags=['task_deco_DAG'],
)
def taskflow_x():

    # Tarefa definida com o PythonOperator
    task_e_operator = PythonOperator(
        task_id='task_e',  # ID da tarefa
        python_callable=_task_e,  # Função Python chamada pela tarefa
    )

    # Tarefa definida com o decorador @task
    @task
    def task_f(value):
        print("Task F")
        print(f"Valor recebido de task_e: {value}")

    # Chama task_f e passa o valor retornado por task_e através do XCom
    task_f(task_e_operator.output)

# Chamando a função 'taskflow_x' para criar a DAG
taskflow_x()
