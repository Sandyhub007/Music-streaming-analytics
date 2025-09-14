from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_data_quality_checks():
    """Run Great Expectations data quality checks"""
    import great_expectations as gx
    print("Running data quality checks...")
    # Add your GX validation logic here
    return "Data quality checks completed"

def process_streaming_analytics():
    """Trigger Spark streaming job"""
    import subprocess
    print("Starting Spark streaming analytics...")
    # Add logic to trigger Spark jobs
    return "Spark job initiated"

def update_dashboards():
    """Refresh PowerBI dashboards"""
    print("Updating PowerBI dashboards...")
    # Add PowerBI refresh logic
    return "Dashboards updated"

# Define the DAG
dag = DAG(
    'music_streaming_analytics',
    default_args=default_args,
    description='Music streaming analytics pipeline',
    schedule_interval='@hourly',
    catchup=False,
    tags=['music', 'analytics', 'streaming'],
)

# Define tasks
data_quality_task = PythonOperator(
    task_id='run_data_quality_checks',
    python_callable=run_data_quality_checks,
    dag=dag,
)

spark_analytics_task = PythonOperator(
    task_id='process_streaming_analytics',
    python_callable=process_streaming_analytics,
    dag=dag,
)

dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/dags/analytics/dbt && dbt run --profiles-dir .',
    dag=dag,
)

dbt_test_task = BashOperator(
    task_id='test_dbt_models',
    bash_command='cd /opt/airflow/dags/analytics/dbt && dbt test --profiles-dir .',
    dag=dag,
)

dashboard_update_task = PythonOperator(
    task_id='update_dashboards',
    python_callable=update_dashboards,
    dag=dag,
)

# Set task dependencies
data_quality_task >> spark_analytics_task >> dbt_run_task >> dbt_test_task >> dashboard_update_task
