import requests
import asyncio
import time
from pyspark.sql import SparkSession
from pyspark import SparkConf
import matplotlib.pyplot as plt
import streamlit as st

# Initialize Streamlit page configuration
st.set_page_config(page_title="Currency Price Change (BTCtoUSD)", layout="wide")

# Initialize SparkConf object
conf = SparkConf()

# Set configurations for Spark to connect to Elasticsearch
conf.set("spark.driver.extraClassPath", "C:/spark353/jars/elasticsearch-spark-30_2.12-8.16.0.jar")
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

# Function to read data from Elasticsearch and return the DataFrame
async def get_data_from_elasticsearch():
    df = spark.read \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", my_resource) \
        .option("es.query", my_query) \
        .load()

    return df.toPandas()  # Return as pandas DataFrame for easy manipulation

plot_placeholder = st.empty()
table_placeholder = st.empty()
fetch_count_placeholder = st.empty()
# Create columns for layout
col1, col2 = st.columns([10, 1])  # Adjust the ratio of columns (3:1 for plot and additional info)

fetch_count = 1
# Left column for plot
with col1:
    # Button to trigger data fetch and plot update
    if st.button('Start getting data'):
        # Fetch data from Elasticsearch
        while True:
                
            pandas_df = asyncio.run(get_data_from_elasticsearch())

            if not pandas_df.empty:
                fetch_count +=1 
                # Extract price data and convert to float
                prices = pandas_df['price'].astype(float)  # Ensure 'price' is float for plotting
                pandas_df['fetch_count'] = fetch_count

                # Plot the data by order
                fig, ax = plt.subplots(figsize=(8, 4))  # Adjust figure size for a more compact chart
                ax.plot(prices, label='Price', color='green')
                ax.set_title('Currency Price Change', fontsize=14)
                ax.set_xlabel('Order', fontsize=12)
                ax.set_ylabel('Price ($)', fontsize=12)

                # Add tighter padding around the plot
                plt.tight_layout()

                # Show the plot in Streamlit
                plot_placeholder.pyplot(fig)
                table_placeholder.write(pandas_df)
                fetch_count_placeholder.write(f"Data fetched {fetch_count}")
            else:
                st.write("No data found in Elasticsearch.")
            time.sleep(10)

# Optional: Stop the Spark session
# spark.stop()
