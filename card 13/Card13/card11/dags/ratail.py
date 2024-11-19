from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 11, 1),
     schedule='@daily',
     catchup=False,
     tags=['test']
)

def retail():
    @task
    def start():
        print('Hi')
        
    start()
    
retail()