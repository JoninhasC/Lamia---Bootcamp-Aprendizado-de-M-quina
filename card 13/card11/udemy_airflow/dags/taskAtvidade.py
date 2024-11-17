# Transforme um DAG Airflow básico com duas tarefas compartilhando dados
# XComs em um DAG equivalente usando a API TaskFlow.
# O DAG original gera um número aleatório e determina se é par ou ímpar.
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime
# import random
#
# def _generate_random_number(ti):
#     number = random.randint(1, 100)  # Gera um número aleatório entre 1 e 100
#     ti.xcom_push(key="random_number", value=number)  # Envia o número gerado via XCom
#     print(ti.xcom_push(key="random_number", value=number))
#
# def _check_even_odd(ti):
#     number = ti.xcom_pull(task_ids="generate_number", key="random_number")  # Recupera o número gerado
#     if number % 2 == 0:
#         print(f"The number {number} is Even")
#     else:
#         print(f"The number {number} is Odd")
# 
# with DAG(
#     dag_id="taskAtividade01",  # Nome do DAG
#     start_date=datetime(2024, 11, 16),  # Data de início do DAG
#     schedule_interval="@daily",  # Executa diariamente
#     catchup=False,  # Não executa tarefas retroativas
#     tags=["taskAtividade01"],
# ) as dag:
#     generate_number = PythonOperator(
#         task_id="generate_number",  # Nome da tarefa
#         python_callable=_generate_random_number,  # Função chamada pela tarefa
#     )
#
#     check_even_odd = PythonOperator(
#         task_id="check_even_odd",  # Nome da tarefa
#         python_callable=_check_even_odd,  # Função chamada pela tarefa
#     )
#
#     generate_number >> check_even_odd  # Define a ordem de execução das tarefas
#
#
#
# Importing necessary libraries
from airflow.decorators import dag, task
from datetime import datetime
import random

# Define the DAG with the @dag decorator
@dag(
    dag_id='taskResult',  # Unique ID for the DAG
    start_date=datetime(2024, 11, 16),  # Start date for the DAG
    schedule_interval='@daily',  # Schedule to run daily
    catchup=False,  # Do not run for past dates
    tags=['taskResult'],  # Tags for categorization
)
def taskflow_even_or_odd():

    # Task to generate a random number
    @task
    def generate_random_number():
        number = random.randint(1, 100)  # Generate a random integer between 1 and 100
        print(f"Generated number: {number}")
        return number  # Return the number to be used by the next task

    # Task to check if the number is even or odd
    @task
    def check_even_odd(number: int):
        if number % 2 == 0:
            print(f"The number {number} is Even")
        else:
            print(f"The number {number} is Odd")

    # Calling tasks and defining their order
    random_number = generate_random_number()  # Call the first task
    check_even_odd(random_number)  # Use the output of the first task as input for the second

# Call the function to define the DAG
taskflow_even_or_odd()


