# Importando o decorator `dag` do módulo `airflow.decorators`
# O `dag` é utilizado para definir uma DAG no Airflow, que é uma coleção de tarefas (tasks) que devem ser executadas de maneira ordenada.
from airflow.decorators import dag

# Importando o módulo `datetime` da biblioteca padrão do Python.
# `datetime` é usado para manipulação de datas e horas. Aqui, ele nos permite definir a data de início para a execução da DAG.
from datetime import datetime

# Decorator @dag é usado para definir a DAG (Directed Acyclic Graph) no Airflow.
# Esse decorator transforma a função em uma DAG, fornecendo parâmetros essenciais para a configuração da execução da DAG.

@dag(
    # O parâmetro `start_date` define a data e hora em que a DAG começará a ser executada.
    # Aqui, a DAG começará a rodar a partir de 1º de janeiro de 2024.
    start_date=datetime(2024, 1, 1),

    # O parâmetro `schedule` define a frequência de execução da DAG.
    # O valor `@daily` indica que a DAG será executada uma vez por dia, à meia-noite.
    schedule='@daily',

    # O parâmetro `catchup` determina se o Airflow deve ou não rodar as tarefas pendentes caso o scheduler não tenha conseguido executá-las em um dado dia.
    # `catchup=False` indica que o Airflow não deve executar tarefas retroativas, ou seja, ele começará a execução a partir do `start_date` e continuará daqui em diante.
    catchup=False,

    # O parâmetro `tags` é utilizado para adicionar rótulos à DAG.
    # Isso é útil para categorizar e organizar as DAGs, especialmente quando você tem muitas no ambiente do Airflow.
    tags=['stock_market']
)
# Definição da função que representa a DAG. A função é decorada com o `@dag`, o que a torna uma DAG.
# O nome dessa função pode ser qualquer nome, mas neste caso, optamos por `stock_market` para refletir o objetivo da DAG (trabalhar com dados do mercado de ações).
def stock_market():
    # Dentro da função, você definiria as tarefas (tasks) que a DAG vai executar.
    # No momento, não há nenhuma tarefa definida dentro da função, então a DAG não está realizando nada ainda.
    # Quando as tarefas forem definidas, elas são colocadas aqui dentro.
    pass

# Chamando a função `stock_market()` para efetivamente criar a DAG.
# Sem esta chamada, a DAG não seria registrada no Airflow.
# A função `stock_market()` é chamada uma vez para criar a DAG, e então ela é executada conforme o agendamento definido no `schedule`.
stock_market()
