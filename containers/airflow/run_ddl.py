from pyspark.sql import SparkSession
from pathlib import Path
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)

# Create Spark session
spark = (
    SparkSession.builder.appName("Recreate TPCH tables & load in data")
    .config("spark.sql.catalogImplementation", "hive")
    .enableHiveSupport()
    .getOrCreate()
)


logger.info("create analytics schema")
spark.sql("CREATE SCHEMA IF NOT EXISTS analytics")
spark.sql("use analytics")

logger.info("Dropping any existing TPCH tables")
# Drop existing tables if they exist
spark.sql("DROP TABLE IF EXISTS analytics.customer")
spark.sql("DROP TABLE IF EXISTS analytics.lineitem")
spark.sql("DROP TABLE IF EXISTS analytics.nation")
spark.sql("DROP TABLE IF EXISTS analytics.orders")
spark.sql("DROP TABLE IF EXISTS analytics.part")
spark.sql("DROP TABLE IF EXISTS analytics.partsupp")
spark.sql("DROP TABLE IF EXISTS analytics.region")
spark.sql("DROP TABLE IF EXISTS analytics.supplier")


logger.info("Creating TPCH tables")
# Create tables using Iceberg format
spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.customer (
  c_custkey    BIGINT,
  c_name       STRING,
  c_address    STRING,
  c_nationkey  BIGINT,
  c_phone      STRING,
  c_acctbal    DECIMAL(15,2),
  c_mktsegment STRING,
  c_comment    STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.lineitem (
  l_orderkey      BIGINT,
  l_partkey       BIGINT,
  l_suppkey       BIGINT,
  l_linenumber    INT,
  l_quantity      DECIMAL(15,2),
  l_extendedprice DECIMAL(15,2),
  l_discount      DECIMAL(15,2),
  l_tax           DECIMAL(15,2),
  l_returnflag    STRING,
  l_linestatus    STRING,
  l_shipdate      DATE,
  l_commitdate    DATE,
  l_receiptdate   DATE,
  l_shipinstruct  STRING,
  l_shipmode      STRING,
  l_comment       STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.nation (
  n_nationkey INT,
  n_name      STRING,
  n_regionkey INT,
  n_comment   STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.orders (
  o_orderkey      BIGINT,
  o_custkey       BIGINT,
  o_orderstatus   STRING,
  o_totalprice    DECIMAL(15,2),
  o_orderdate     DATE,
  o_orderpriority STRING,
  o_clerk         STRING,
  o_shippriority  INT,
  o_comment       STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.part (
  p_partkey     BIGINT,
  p_name        STRING,
  p_mfgr        STRING,
  p_brand       STRING,
  p_type        STRING,
  p_size        INT,
  p_container   STRING,
  p_retailprice DECIMAL(15,2),
  p_comment     STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.partsupp (
  ps_partkey    BIGINT,
  ps_suppkey    BIGINT,
  ps_availqty   INT,
  ps_supplycost DECIMAL(15,2),
  ps_comment    STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.region (
  r_regionkey INT,
  r_name      STRING,
  r_comment   STRING
) 
""")

spark.sql("""
CREATE TABLE IF NOT EXISTS analytics.supplier (
  s_suppkey   BIGINT,
  s_name      STRING,
  s_address   STRING,
  s_nationkey BIGINT,
  s_phone     STRING,
  s_acctbal   DECIMAL(15,2),
  s_comment   STRING
) 
""")


def upsert_data(
    data_name,
    data_path=Path("/opt/airflow/data"),
):
    csv_path = data_path / f"{data_name}.csv"
    logger.info(f"Reading {data_name} data from {str(csv_path)}")
    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("delimiter", ",")
        .option("inferSchema", "true")
        .load(str(csv_path))
    )
    df.write.mode("overwrite").saveAsTable(f"analytics.{data_name}")


logger.info("Loading data into TPCH Iceberg tables")
upsert_data("customer")
upsert_data("lineitem")
upsert_data("nation")
upsert_data("orders")
upsert_data("part")
upsert_data("partsupp")
upsert_data("region")
upsert_data("supplier")
