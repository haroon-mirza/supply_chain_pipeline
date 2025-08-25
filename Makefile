
####################################################################################################################
# Setup containers to run Airflow

docker-spin-up:
	docker compose build && docker compose up airflow-init && docker compose up --build -d 

perms:
	sudo mkdir -p logs plugins temp dags tests data visualization && sudo chmod -R u=rwx,g=rwx,o=rwx logs plugins temp dags tests data visualization tpch_analytics

do-sleep:
	sleep 30

up: perms docker-spin-up do-sleep

down:
	docker compose down

restart: down up

sh:
	docker exec -ti scheduler bash

dbt-docs:
	docker exec -d webserver bash -c "cd /opt/airflow/tpch_analytics && nohup dbt docs serve --host 0.0.0.0 --port 8081 > /tmp/dbt_docs.log 2>&1"
