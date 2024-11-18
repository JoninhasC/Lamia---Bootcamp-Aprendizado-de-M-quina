from airflow.decorators import dag, task  # Importa os decoradores dag e task para criar DAGs e tarefas de forma mais simples.
from datetime import datetime  # Importa o módulo datetime para trabalhar com datas no Airflow.

# Definição do DAG usando o decorador @dag
@dag(
    start_date=datetime(2024, 11, 17),  # Define a data de início do DAG.
    schedule_interval='@daily',  # Define o intervalo de agendamento do DAG. Neste caso, ele será executado uma vez por dia.
    catchup=False,  # Define que não deve ser feita a execução retroativa para datas passadas, evitando execuções extras.
    tags=['taskExemplo01']  # Atribui uma tag ao DAG para facilitar a organização e filtragem.
)
def task_exemplo01():
    # Definindo a tarefa 'task_c' usando o decorador @task.
    @task
    def task_c():
        print("Task C")  # Imprime "Task C" no log da execução.
        return 412  # Retorna o valor 412, que será passado para outras tarefas.

    # Definindo a tarefa 'task_d' usando o decorador @task. Ela recebe um valor como argumento.
    @task
    def task_d(value):
        print("Task D")  # Imprime "Task D" no log da execução.
        print(f"Valor recebido de task_c: {value}")  # Imprime o valor recebido de 'task_c'.

    # Executa a tarefa task_d, passando o valor retornado pela task_c.
    task_d(task_c())  # Aqui, task_c() é chamada, e o valor retornado é passado como argumento para task_d.

# Invoca o DAG. Essa chamada executa o fluxo de trabalho do DAG.
task_exemplo01()  # Executa a função que define o DAG, criando e agendando as tarefas dentro do DAG.
