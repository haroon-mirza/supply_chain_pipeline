from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

with DAG(
    "generate_customer_marketing_metrics",
    description="A DAG to extract data, load into db and generate customer marketing metrics",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    extract_data = BashOperator(
        task_id="extract_data",
        bash_command="cd $AIRFLOW_HOME && python3 generate_data.py && python3 run_ddl.py",
    )

    transform_data = BashOperator(
        task_id="dbt_run",
        bash_command="cd $AIRFLOW_HOME && dbt run --profiles-dir /opt/airflow/tpch_analytics/ --project-dir /opt/airflow/tpch_analytics/",
    )

    generate_docs = BashOperator(
        task_id="dbt_docs_gen",
        bash_command="cd $AIRFLOW_HOME && dbt docs generate --profiles-dir /opt/airflow/tpch_analytics/ --project-dir /opt/airflow/tpch_analytics/",
    )

    generate_dashboard = BashOperator(
        task_id="generate_dashboard",
        bash_command="cd $AIRFLOW_HOME && python3 /opt/airflow/tpch_analytics/dashboard.py",
    )

    extract_data >> transform_data >> generate_docs >> generate_dashboard
