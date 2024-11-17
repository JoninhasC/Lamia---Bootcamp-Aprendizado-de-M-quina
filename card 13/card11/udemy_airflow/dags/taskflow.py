# Importação necessária para o funcionamento do Airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
# Corrigir a importação do módulo datetime (erro de digitação: 'detetime' → 'datetime')
from datetime import datetime

# Definindo a tarefa '_task_a' que imprime "Task A" e retorna um valor
def _task_a(ti):
    print("Task A")
    return 42  # Retorna o valor 42 que pode ser acessado por outras tarefas


# Definindo a tarefa '_task_b' que imprime "Task B" e busca o retorno de '_task_a' via XCom
def _task_b(ti):
    print("Task B")
    # Usando o ti (Task Instance) para pegar o valor retornado pela tarefa '_task_a'
    print(ti.xcom_pull(task_ids='_task_a'))


# Criando o contexto da DAG
with DAG(
        dag_id='taskflow',  # ID único para a DAG
        start_date=datetime(2024, 12, 3),  # Data de início da DAG
        schedule_interval='@daily',  # Agendamento da DAG (executa uma vez por dia)
        catchup=False,  # Não executar tarefas retroativas
        tags=['taskflow'],  # Tag para categorizar a DAG
) as dag:
    # Definindo as tarefas da DAG com PythonOperator
    _task_a = PythonOperator(
        task_id='_task_a',  # ID único da tarefa
        python_callable=_task_a,  # Função Python que a tarefa irá chamar
    )

    _task_b = PythonOperator(
        task_id='_task_b',  # ID único da tarefa
        python_callable=_task_b,  # Função Python que a tarefa irá chamar
    )


    # Definindo a ordem de execução das tarefas
    _task_a >> _task_b  # A tarefa _task_b será executada após _task_a

