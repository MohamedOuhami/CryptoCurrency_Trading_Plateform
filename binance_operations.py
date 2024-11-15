import requests
from pyspark.sql import SparkSession
from pyspark import SparkConf

# Initialize SparkConf object
conf = SparkConf()

# Set configurations for Spark to connect to Elasticsearch
conf.set("spark.driver.extraClassPath", "C:/spark-3.5.1/jars/elasticsearch-spark-30_2.12-8.16.0.jar")
conf.set("es.nodes", "localhost:9200")  # Ensure Elasticsearch is running on localhost:9200
conf.set("es.nodes.discovery", "false")  # Disable node discovery if needed
conf.set("es.node.data.only", "false")
conf.set("es.net.http.auth.user", "elastic")  # Correct username for authentication
conf.set("es.net.http.auth.pass", "v01d")   # Correct password for authentication
conf.set("es.net.ssl", "false")  # Disable SSL if not required
conf.set("es.nodes.wan.only", "true")  # Disable WAN mode (for local Elasticsearch)


# Create SparkSession with the configured settings
spark = SparkSession.builder \
    .master("local[4]") \
    .appName("testing_elastic_Search") \
    .config(conf=conf) \
    .getOrCreate()

# Define the Elasticsearch resource (index name) and the query (optional)
my_resource = "binance_data"  # Elasticsearch index name (without type, if not using types)
my_query = '{"query":{"match_all": {}}}'  # Elasticsearch query (match all documents)

# Read data from Elasticsearch using the defined resource and query
df = spark.read \
    .format("org.elasticsearch.spark.sql") \
    .option("es.resource", my_resource) \
    .option("es.query", my_query) \
    .load()

# Show the DataFrame content (optional)
df.show()

print(f"The number of entries in the index is {df.count()}")

# Stop the Spark session after completion
spark.stop()