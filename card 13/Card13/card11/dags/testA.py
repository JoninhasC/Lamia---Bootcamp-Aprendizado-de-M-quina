from airflow.decorators import dag, task
from datetime import datetime

@dag(
    start_date=datetime(2021, 11, 1),
     schedule='@weekly',
     tags=['testA'],

     )
def testA():
    @task
    def start():
        print('Hi')

    start()


testA()