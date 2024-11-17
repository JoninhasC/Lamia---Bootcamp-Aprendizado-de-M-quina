# Importando as bibliotecas necessárias do Airflow
from airflow.decorators import dag, task
from datetime import datetime


# Definindo a DAG com o decorador @dag
@dag(
    start_date=datetime(2024, 12, 1),  # Data de início da DAG
    schedule_interval='@daily',  # Agendamento da DAG (executa uma vez por dia)
    catchup=False,  # Não executar tarefas retroativas
    tags=['task_dag_task'],  # Tag para categorizar a DAG
)
def taskflow_dag():
    # Definindo a tarefa 'task_a' que imprime "Task A" e retorna um valor
    @task
    def task_c():
        print("Task c")
        return 42  # Retorna o valor 42 que pode ser acessado por outras tarefas

    # Definindo a tarefa 'task_b' que imprime "Task B" e busca o retorno de 'task_a' via XCom
    @task
    def task_d(value):
        print("Task d")
        # Aqui, estamos puxando o valor de 'task_a' com XCom
        print(value)

    # Chama a tarefa 'task_a' e passa seu retorno para 'task_b'
    task_d(task_c())

# Chamando a função 'taskflow' para criar a DAG
taskflow_dag()
