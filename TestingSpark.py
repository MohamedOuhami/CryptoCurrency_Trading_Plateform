import asyncio
import time
from pyspark.sql import SparkSession
from pyspark import SparkConf
import pandas as pd

# Initialize Streamlit page configuration

# Initialize SparkConf object
# conf = SparkConf()
# conf.set("spark.driver.extraClassPath",
#         "C:/spark-3.5.3-bin-hadoop3/jars/elasticsearch-spark-30_2.12-8.16.0.jar")
# conf.set("spark.executor.extraClassPath",
#        "C:/spark-3.5.3-bin-hadoop3/jars/elasticsearch-spark-30_2.12-8.16.0.jar")

# conf.set("es.nodes", "172.19.0.5:9200")
# conf.set("es.nodes", "172.19.0.6:9200")
# conf.set("es.nodes.discovery", "false")
# conf.set("es.node.data.only", "false")
# conf.set("es.net.http.auth.user", "elastic")
# conf.set("es.net.http.auth.pass", "v01d")
# conf.set("es.net.ssl", "false")
# conf.set("es.nodes.wan.only", "true")
# conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

# Set memory configurations
# conf.set("spark.executor.memory", "4g")  # 4GB for executors
# conf.set("spark.driver.memory", "4g")    # 4GB for the driver

# Create SparkSession
from pyspark.sql import SparkSession
from pyspark import SparkConf

# Create SparkConf with the appropriate configurations
conf = SparkConf()
conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
conf.set("spark.es.index.auto.create", "true")
conf.set("spark.es.nodes", "es01")
conf.set("spark.es.port", "9200")
conf.set("spark.es.net.http.auth.user", "elastic")
conf.set("spark.es.net.http.auth.pass", "v01d")
conf.set("spark.es.resource", "binance_data")
conf.set("spark.es.nodes.wan.only", "true")
# Allocate 4GB of memory for the executors
conf.set("spark.executor.memory", "4g")
conf.set("spark.driver.memory", "4g")  # Allocate 4GB of memory for the driver

# Build SparkSession with the configured SparkConf
# Now you can use sparkSession for your operations

sparkSession = SparkSession.builder \
    .master("local[*]") \
    .appName("testing_elastic_search") \
    .config(conf=conf) \
    .getOrCreate()
# Elasticsearch resource and query
my_resource = "binance_data"
my_query = '{"query":{"match_all": {}}}'

# Function to fetch data from Elasticsearch


def get_data_from_elasticsearch():
    df = sparkSession.read \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", my_resource) \
        .option("es.query", my_query) \
        .load()
    return df.toPandas()  # Convert to pandas DataFrame


print(get_data_from_elasticsearch())
