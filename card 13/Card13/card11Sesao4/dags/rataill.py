from airflow.decorators import dag, task
from datetime import datetime


@dag(start_date=datetime(2024, 11, 18),
     schedule='@daily',
     catchup=True,
     tags=['test']
     )
def retail(retries=15):
    @task
    def start():
        print('Hi')
        raise ValueError('Error')

    start()


retail()