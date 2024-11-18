from airflow.decorators import dag, task
from datetime import datetime
import random

# Definindo o DAG com o decorador @dag
@dag(
    dag_id='random_number_checker',
    start_date=datetime(2024, 11, 17),
    schedule="@daily",  # O DAG será executado uma vez por dia
    description='A simple DAG to generate and check random numbers',
    catchup=False,
    tags=['random_number_checker']
)
def random_number_checker():

    # Definindo a tarefa que gera um número aleatório
    @task
    def generate_random_number():
        number = random.randint(1, 100)  # Gera um número aleatório entre 1 e 100
        print(f"Generated random number: {number}")  # Imprime o número gerado
        return number  # Retorna o número gerado, que será automaticamente passado para a próxima tarefa

    # Definindo a tarefa que verifica se o número gerado é par ou ímpar
    @task
    def check_even_odd(number: int):
        result = "even" if number % 2 == 0 else "odd"  # Verifica se o número é par ou ímpar
        print(f"The number {number} is {result}.")  # Imprime o resultado

    # Chama as tarefas em sequência, passando os valores automaticamente
    number = generate_random_number()  # Gera o número aleatório
    check_even_odd(number)  # Verifica se o número gerado é par ou ímpar

# Chamando a função para criar o DAG
random_number_checker()
