from airflow import DAG  # Importa a classe DAG do Airflow, usada para definir o fluxo de trabalho.
from airflow.operators.python import PythonOperator  # Importa o operador PythonOperator para rodar funções Python dentro do DAG.
from datetime import datetime  # Importa o módulo datetime para definir datas no DAG.

# Função que será executada pela tarefa _task_a
def _task_a():
    print("A")  # Imprime "A" no log da execução.
    return 42  # Retorna o valor 42, que será usado por outras tarefas.

# Função que será executada pela tarefa _task_b
def _task_b(ti=None):  # O parâmetro ti é a instância de TaskInstance, usado para interagir com o XCom.
    print("B")  # Imprime "B" no log da execução.
    # Puxa o valor retornado pela tarefa 'task_a' através do XCom (método xcom_pull).
    print(ti.xcom_pull(task_ids='task_a'))  # Acessa o valor retornado de _task_a (42) e imprime.

# Definindo o DAG com seus parâmetros
with DAG(
    dag_id='task_exemplo',  # Identificador único para o DAG.
    start_date=datetime(2024, 11, 17),  # Data de início da execução do DAG.
    schedule_interval='@daily',  # Intervalo de execução, que será diário neste caso.
    catchup=False,  # Define que o DAG não deve tentar executar tarefas perdidas para datas passadas.
    tags=['task_exemplo'],  # Adiciona uma tag ao DAG para categorização.
) as dag:  # Contexto do DAG sendo utilizado para definir tarefas dentro do escopo.

    # Definindo a tarefa _task_a
    _task_a = PythonOperator(
        task_id='task_a',  # ID único da tarefa.
        python_callable=_task_a,  # Função Python que será chamada para esta tarefa.
    )

    # Definindo a tarefa _task_b
    _task_b = PythonOperator(
        task_id='task_b',  # ID único da tarefa.
        python_callable=_task_b,  # Função Python que será chamada para esta tarefa.
    )

    # Definindo a dependência entre as tarefas: _task_b só executa após _task_a ser concluída.
    _task_a >> _task_b  # Isso estabelece que _task_b depende de _task_a. Ou seja, _task_b será executada depois de _task_a.
