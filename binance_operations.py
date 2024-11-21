import asyncio
import time
import matplotlib.pyplot as plt
import streamlit as st
from pyspark.sql import SparkSession
from pyspark import SparkConf
import pandas as pd

# Initialize Streamlit page configuration
st.set_page_config(page_title="Currency Price Change", layout="wide")

# Initialize SparkConf object
conf = SparkConf()
conf.set("spark.driver.extraClassPath", "C:/spark353/jars/elasticsearch-spark-30_2.12-8.16.0.jar")
conf.set("es.nodes", "localhost:9200")
conf.set("es.nodes.discovery", "false")
conf.set("es.node.data.only", "false")
conf.set("es.net.http.auth.user", "elastic")
conf.set("es.net.http.auth.pass", "v01d")
conf.set("es.net.ssl", "false")
conf.set("es.nodes.wan.only", "true")

# Create SparkSession
spark = SparkSession.builder \
    .master("local[4]") \
    .appName("testing_elastic_search") \
    .config(conf=conf) \
    .getOrCreate()

# Elasticsearch resource and query
my_resource = "binance_data"
my_query = '{"query":{"match_all": {}}}'

# Function to fetch data from Elasticsearch
def get_data_from_elasticsearch():
    df = spark.read \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", my_resource) \
        .option("es.query", my_query) \
        .load()
    return df.toPandas()  # Convert to pandas DataFrame

# Initialize session state
if 'symbol_data' not in st.session_state:
    st.session_state['symbol_data'] = {}
if 'symbols' not in st.session_state:
    st.session_state['symbols'] = []
if 'previous_symbol' not in st.session_state:
    st.session_state['previous_symbol'] = None  # Track the last selected symbol

# Sidebar for controls and table display
st.sidebar.header("Controls")
table_placeholder = st.sidebar.empty()

# Dropdown for selecting refresh interval
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", min_value=1, max_value=30, value=10)

# Dropdown for selecting symbol (in the sidebar)
selected_symbol = st.sidebar.selectbox("Select Symbol", st.session_state['symbols'])

# Placeholder for the plot
st.title("Real-Time Currency Price Dashboard")
plot_placeholder = st.empty()

# Function to process and update session state with new data
def process_data():
    pandas_df = get_data_from_elasticsearch()
    if not pandas_df.empty:
        grouped_data = pandas_df.groupby('symbol')
        for symbol, group in grouped_data:
            if symbol not in st.session_state['symbol_data']:
                st.session_state['symbol_data'][symbol] = []
            st.session_state['symbol_data'][symbol].extend(group['price'].astype(float).tolist())
            if len(st.session_state['symbol_data'][symbol]) > 100:
                st.session_state['symbol_data'][symbol] = st.session_state['symbol_data'][symbol][-100:]
        st.session_state['symbols'] = list(st.session_state['symbol_data'].keys())
    return pandas_df

# Function to update the graph and table
def update_dashboard():
    data = process_data()
    if selected_symbol and selected_symbol in st.session_state['symbol_data']:
        # Update graph
        with plot_placeholder.container():
            fig, ax = plt.subplots(figsize=(10, 5))
            prices = st.session_state['symbol_data'][selected_symbol]

            # Iterate through the price data to plot the candles
            for i in range(1, len(prices)):
                # Color bar green if price increased, red if decreased
                color = 'green' if prices[i] >= prices[i - 1] else 'red'
                
                # Plot a vertical line (like a candlestick)
                ax.vlines(i, prices[i - 1], prices[i], color=color, lw=3)
            
            ax.set_title(f'Currency Price Change: {selected_symbol}', fontsize=10)
            ax.set_xlabel('', fontsize=8)
            ax.set_ylabel('Price ($)', fontsize=8)
            ax.grid(True)
            plt.tight_layout()
            st.pyplot(fig)  # Display the figure in Streamlit
            plt.close(fig)

        # Update table in the sidebar
        filtered_df = data[data['symbol'] == selected_symbol]
        table_placeholder.dataframe(filtered_df)

    else:
        with plot_placeholder.container():
            st.warning("Selected symbol has no data.")
            table_placeholder.empty()  # Clear the table if no data is available

# Live update simulation based on refresh interval
while True:
    update_dashboard()
    time.sleep(refresh_interval)
