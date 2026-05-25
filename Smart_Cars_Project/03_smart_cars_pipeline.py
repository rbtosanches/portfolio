# # DAG Airflow — Carga CSV → PostgreSQL → DBT Run → DBT Test

# Esta DAG realiza:

# 1. Leitura do CSV `pickup_sales_dataset.csv`
# 2. Criação automática da tabela `pickup_sales` no PostgreSQL
# 3. Carga dos dados para o PostgreSQL
# 4. Execução do `dbt run`
# 5. Execução do `dbt test`

# # Instalação de dependências
# pip install pandas sqlalchemy psycopg2-binary apache-airflow
# pip install dbt-postgres

from datetime import datetime

import pandas as pd
from airflow import DAG
from airflow.hooks.base import BaseHook

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from sqlalchemy import create_engine, text

# =========================================================
# CONFIGURAÇÕES
# =========================================================

CSV_FILE = "/opt/airflow/data/pickup_sales_dataset.csv"
# CSV_FILE = "/home/sanches/pickups_pipeline/data/pickup_sales_dataset.csv"
TABLE_NAME = "raw_pickup_sales"

DBT_PROJECT_DIR = "/opt/airflow/dbt/pickup_project"
DBT_PROFILES_DIR = "/opt/airflow/dbt/pickup_project"

# =========================================================
# FUNÇÃO DE CARGA
# =========================================================


def load_csv_to_postgres():
    print("Iniciando carga do CSV...")

    # =====================================================
    # CONNECTION AIRFLOW
    # =====================================================

    conn = BaseHook.get_connection("postgres_pickup")

    DATABASE_URL = (
        f"postgresql+psycopg2://{conn.login}:{conn.password}"
        f"@{conn.host}:{conn.port}/{conn.schema}"
    )

    # DATABASE_URL = (
    #     f"postgresql+psycopg2://{conn.login}:beta2020"
    #     f"@{conn.host}:{conn.port}/{conn.schema}"
    # )

    engine = create_engine(DATABASE_URL)

    # =====================================================
    # LEITURA CSV
    # =====================================================

    df = pd.read_csv(
        CSV_FILE,
        sep=";",
        dtype=str
        # parse_dates=["sale_date"]
    )

    # print(df.head(2))

    # =====================================================
    # AJUSTES DE TIPOS
    # =====================================================

    # df["year"] = df["year"].astype(int)
    # df["month"] = df["month"].astype(int)
    # df["installments"] = df["installments"].astype(int)

    # =====================================================
    # CREATE SCHEMAS
    # =====================================================

    create_bronze_sql = """CREATE SCHEMA IF NOT EXISTS bronze;"""
    with engine.begin() as connection:
        connection.execute(text(create_bronze_sql))

    create_silver_sql = """CREATE SCHEMA IF NOT EXISTS silver;"""
    with engine.begin() as connection:
        connection.execute(text(create_silver_sql))

    create_gold_sql = """CREATE SCHEMA IF NOT EXISTS gold;"""
    with engine.begin() as connection:
        connection.execute(text(create_gold_sql))

    # =====================================================
    # CREATE TABLE
    # =====================================================

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS bronze.{TABLE_NAME} (
        sale_date TEXT,
        year TEXT,
        month TEXT,
        customer_id VARCHAR(50),
        city VARCHAR(100),
        model VARCHAR(50),
        list_price TEXT,
        salesperson VARCHAR(50),
        sales_target TEXT,
        installments TEXT,
        discount_pct TEXT,
        discount_value TEXT,
        gifts VARCHAR(255),
        gift_cost TEXT,
        gross_revenue TEXT,
        net_margin TEXT
    );
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_sql))

    print("Tabela criada/verificada com sucesso.")

    # =====================================================
    # TRUNCATE OPCIONAL
    # =====================================================

    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE bronze.{TABLE_NAME};"))

    print("Tabela truncada.")

    # =====================================================
    # INSERT DADOS
    # =====================================================

    df.to_sql(
        TABLE_NAME,
        engine,
        schema="bronze",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

    # df.to_sql(
    # "pickup_sales",
    # engine,
    # schema="bronze",
    # if_exists="append",
    # index=False
    # )

    print(f"Carga concluída. Registros inseridos: {len(df)}")


# =========================================================
# DAG
# =========================================================

with DAG(
    dag_id="pickup_sales_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["postgres", "dbt", "sales", "pickup"],
) as dag:

    # =====================================================
    # TASK - LOAD CSV
    # =====================================================

    load_csv_task = PythonOperator(
        task_id="load_csv_to_postgres",
        python_callable=load_csv_to_postgres,
    )

    # =====================================================
    # TASK - DBT RUN
    # =====================================================

    # dbt_run_task = BashOperator(
    #     task_id="dbt_run",
    #     bash_command=(
    #         f"cd {DBT_PROJECT_DIR} && "
    #         f"dbt run --profiles-dir {DBT_PROFILES_DIR}"
    #     ),
    # )

    # =====================================================
    # TASK - DBT TEST
    # =====================================================

    # dbt_test_task = BashOperator(
    #     task_id="dbt_test",
    #     bash_command=(
    #         f"cd {DBT_PROJECT_DIR} && "
    #         f"dbt test --profiles-dir {DBT_PROFILES_DIR}"
    #     ),
    # )

    # =====================================================
    # PIPELINE
    # =====================================================

    load_csv_task
    # load_csv_task >> dbt_run_task >> dbt_test_task
#
# # Exemplo de profiles.yml do DBT
# pickup_project:
#   target: dev

#   outputs:
#     dev:
#       type: postgres
#       host: localhost
#       user: postgres
#       password: sua_senha
#       port: 5432
#       dbname: seu_banco
#       schema: public
#       threads: 4

# # Exemplo de execução local do DBT

# cd /opt/airflow/dbt/pickup_project

# # executar modelos
# DBT_PROFILES_DIR=. dbt run

# # executar testes
# DBT_PROFILES_DIR=. dbt test

# # Fluxo da DAG

# CSV
#   ↓
# PostgreSQL RAW (pickup_sales)
#   ↓
# dbt run
#   ↓
# dbt test

# # Melhorias recomendadas

# ## Data Quality

# Adicionar testes DBT:

# * not_null
# * unique
# * accepted_values
# * relationships
# * freshness

# ---

# ## Observabilidade

# Adicionar:

# * logs estruturados
# * métricas de volume
# * contagem de erros
# * alertas Slack/Teams

# ---

# ## Performance

# Para grandes volumes:

# * COPY do PostgreSQL
# * particionamento
# * índices
# * staging tables
# * carga incremental DBT

# ---

# # Exemplo de comando COPY (mais rápido)

# Alternativa ao `to_sql`:

# ```sql
# COPY pickup_sales
# FROM '/tmp/pickup_sales_dataset.csv'
# DELIMITER ';'
# CSV HEADER;
# ```

# ---

# # Resultado esperado

# Pipeline automatizado:

# ```text
# CSV → PostgreSQL RAW → DBT Models → DBT Tests
# ```

# Pronto para evoluir para:

# * arquitetura medalhão
# * data warehouse
# * data marts
# * CI/CD analytics engineering
# * observabilidade de dados
# * data quality enterprise
