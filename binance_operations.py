import asyncio
import time
import matplotlib.pyplot as plt
import streamlit as st
from pyspark.sql import SparkSession
from pyspark import SparkConf
import pandas as pd

# Initialize Streamlit page configuration
st.set_page_config(page_title="INVESTLY",page_icon="📊",layout="wide")

# Initialize SparkConf object
conf = SparkConf()
conf.set("spark.driver.extraClassPath",
         "C:/spark353/jars/elasticsearch-spark-30_2.12-8.16.0.jar")
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
    # Track the last selected symbol
    st.session_state['previous_symbol'] = None

# Sidebar for controls and table display
# Sidebar for website name with colored letters and white border
st.sidebar.markdown(
    """
    <h1 style='text-align: center; font-weight: bold; font-size: 70px; font-family: Impact; 
               text-shadow: 1px 1px 0px white, -1px -1px 0px white, 1px -1px 0px white, -1px 1px 0px white;'>
        <span style="color: red;">INVE</span><span style="color: green;">STLY</span>
    </h1>
    """, 
    unsafe_allow_html=True
)
st.sidebar.header("Controls")
table_placeholder = st.sidebar.empty()

# Dropdown for selecting refresh interval
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=30, value=10, step=1)

# Dropdown for selecting symbol (in the sidebar)
selected_symbol = st.sidebar.selectbox(
    "Select Symbol", st.session_state['symbols'])

selected_strategy = st.sidebar.radio(
    "Select Trading Strategy",
    ("Moving Averages", 'RSI', "Bollinger Bands"),
    key="strategy"
)
# Placeholder for the plot
st.title("Dashboard")
plot_placeholder1 = st.empty()
plot_placeholder2 = st.empty()
plot_placeholder3 = st.empty()

# Function to process and update session state with new data
def process_data():
    pandas_df = get_data_from_elasticsearch()
    if not pandas_df.empty:
        grouped_data = pandas_df.groupby('symbol')
        for symbol, group in grouped_data:
            if symbol not in st.session_state['symbol_data']:
                st.session_state['symbol_data'][symbol] = []
            st.session_state['symbol_data'][symbol].extend(
                group['price'].astype(float).tolist())
            if len(st.session_state['symbol_data'][symbol]) > 100:
                st.session_state['symbol_data'][symbol] = st.session_state['symbol_data'][symbol][-100:]
        st.session_state['symbols'] = list(
            st.session_state['symbol_data'].keys())
    return pandas_df


def calculate_ma(prices, short_window=10, long_window=50):
    """
    Calculates both the short-term and long-term moving averages
        """
    short_ma = prices.rolling(window=short_window).mean()
    long_ma = prices.rolling(window=long_window).mean()

    return short_ma, long_ma


def generate_signals(short_ma, long_ma):
    """
    Generating the buy and sell signals based on the double ma
        """
    signals = []
    for i in range(1, len(short_ma)):
        if short_ma[i] > long_ma[i] and short_ma[i-1] <= long_ma[i-1]:
            signals.append('Buy')
        elif short_ma[i] < long_ma[i] and short_ma[i-1] >= long_ma[i-1]:
            signals.append("Sell")
        else:
            signals.append("Hold")
    return ["Hold"] + signals

# TODO : Implement the RSI index


def calculate_rsi(prices, window=14):

    # Calculate the daily prices changes
    prices = pd.Series(prices)
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain/loss
    rsi = 100 - (100 / (1+rs))

    return rsi
# TODO : Implement the bollinger bands strategy


def calculate_bollinger_bands(prices, window=20, num_std_dev=2):
    # Ensure prices is a Pandas Series
    prices = pd.Series(prices)

    # Calculate the moving average
    middle_band = prices.rolling(window=window).mean()

    # Calculate the standard deviation
    std_dev = prices.rolling(window=window).std()

    # Calculate the upper and lower bands
    upper_band = middle_band + (num_std_dev * std_dev)
    lower_band = middle_band - (num_std_dev * std_dev)

    return middle_band, upper_band, lower_band


def generate_bollinger_signals(prices, upper_band, lower_band):
    signals = []
    for i in range(1, len(prices)):
        if prices[i] < lower_band[i] and prices[i - 1] > lower_band[i - 1]:
            signals.append("Buy")
        elif prices[i] > upper_band[i] and prices[i - 1] < upper_band[i - 1]:
            signals.append("Sell")
        else:
            signals.append("Hold")
    return signals


def simulate_trading(prices, signals, initial_investment=1000):
    cash = initial_investment  # Starting cash
    portfolio = 0  # Cryptocurrency amount the user owns
    trade_history = []  # Keep track of trade actions

    # Start the simulation
    for i, signal in enumerate(signals):
        if signal == "Buy" and cash > 0:  # Buy when signal is 'Buy'
            # Buy cryptocurrency at the current price
            portfolio = cash / prices[i]
            cash = 0  # All cash is used to buy
            trade_history.append(
                {"Action": "Buy", "Price": prices[i], "Portfolio": portfolio, "Cash": cash})
        elif signal == "Sell" and portfolio > 0:  # Sell when signal is 'Sell'
            # Sell cryptocurrency at the current price
            cash = portfolio * prices[i]
            portfolio = 0  # No more cryptocurrency left
            trade_history.append(
                {"Action": "Sell", "Price": prices[i], "Portfolio": portfolio, "Cash": cash})

    # Final portfolio value (either in cash or cryptocurrency)
    final_value = cash if portfolio == 0 else portfolio * prices[-1]
    return final_value, trade_history


# Sidebar for user input, including initial investment
initial_investment = st.sidebar.number_input(
    "Initial Investment ($)", value=1000, min_value=1, key="investment")


def update_dashboard():
    data = process_data()

    # Ensure selected_symbol is properly initialized and exists in the data
    if selected_symbol and selected_symbol in st.session_state['symbol_data']:
        # Get prices for the selected symbol
        prices = st.session_state['symbol_data'][selected_symbol]

        # Calculate moving averages and signals
        prices_series = pd.Series(prices)
        if selected_strategy == "Moving Averages":
            short_ma, long_ma = calculate_ma(prices_series)
            signals = generate_signals(short_ma, long_ma)
        elif selected_strategy == "Bollinger Bands":
            middle_band, upper_band, lower_band = calculate_bollinger_bands(prices_series)
            signals = generate_bollinger_signals(prices_series, upper_band, lower_band)
        elif selected_strategy == 'RSI':
            rsi = calculate_rsi(prices)
            signals = ["Buy" if rsi[i] < 30 else "Sell" if rsi[i] > 70 else "Hold" for i in range(len(rsi))]

        # Simulate trading based on signals and initial investment
        final_value, trade_history = simulate_trading(prices, signals, initial_investment)

        # Save investment data in session state
        st.session_state['final_value'] = final_value
        st.session_state['trade_history'] = pd.DataFrame(trade_history)

        # Plot the data
        with plot_placeholder1.container():
            st.header("Moving Averages")
            st.markdown("### Moving averages are statistical calculations used to smooth out short-term fluctuations and highlight longer-term trends in data. This plot shows the short (10) and long (50) moving averages for the selected symbol to help identify trends.")
            fig, ax = plt.subplots(figsize=(7, 4))

            # Plot price data as candlesticks
            for i in range(1, len(prices)):
                color = 'green' if prices[i] >= prices[i - 1] else 'red'
                ax.vlines(i, min(prices[i], prices[i - 1]), max(prices[i], prices[i - 1]), color=color, lw=3)

            # Plot moving averages
            ax.plot(short_ma, label="Short MA (10)", color='blue', alpha=0.8)
            ax.plot(long_ma, label="Long MA (50)", color='red', alpha=0.8)

            # Plot buy and sell signals
            buy_signals = [i for i, signal in enumerate(signals) if signal == 'Buy']
            sell_signals = [i for i, signal in enumerate(signals) if signal == 'Sell']
            ax.scatter(buy_signals, [prices[i] for i in buy_signals], marker='^', color='green', label='Buy Signal', alpha=1)
            ax.scatter(sell_signals, [prices[i] for i in sell_signals], marker='v', color='red', label='Sell Signal', alpha=1)

            # Set plot details
            ax.set_title(f'{selected_symbol} Price Change', fontsize=10)
            ax.set_xlabel('Time', fontsize=8)
            ax.set_ylabel('Price ($)', fontsize=8)
            ax.grid(True)
            ax.legend(fontsize=8)

            # Layout adjustment
            plt.tight_layout()

            # Display the figure in Streamlit
            st.pyplot(fig)
            plt.close(fig)

        with plot_placeholder2.container():
            st.header("Relative Strength Index (RSI)")
            st.markdown("### The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. This plot shows the RSI, indicating overbought (70) and oversold (30) conditions, useful for spotting potential trend reversals")
            fig, ax = plt.subplots(figsize=(7, 2))

            # RSI Plot
            rsi = calculate_rsi(prices)
            ax.plot(rsi, label="RSI", color='purple', lw=1.5)
            ax.axhline(70, color='red', linestyle='--', label='Overbought (70)')
            ax.axhline(30, color='green', linestyle='--', label='Oversold (30)')
            ax.set_title('Relative Strength Index (RSI)', fontsize=12)
            ax.set_xlabel('Time', fontsize=10)
            ax.set_ylabel('RSI', fontsize=10)
            ax.grid(True)
            ax.legend(fontsize=8)

            # Layout adjustment
            plt.tight_layout()

            # Display the figure in Streamlit
            st.pyplot(fig)
            plt.close(fig)


        with plot_placeholder3.container(): 
            st.header("Bollinger Bands Strategy")
            st.markdown("### Bollinger Bands are a volatility indicator that consists of a middle band (SMA), an upper band, and a lower band, which are used to assess price volatility. This plot displays the Bollinger Bands (upper, lower, and middle) along with buy/sell signals based on price action within the bands.")

            fig, ax = plt.subplots(figsize=(7, 4))

            # Bollinger Bands Plot
            middle_band, upper_band, lower_band = calculate_bollinger_bands(prices_series)
            bollinger_signals = generate_bollinger_signals(prices_series, upper_band, lower_band)
            ax.plot(prices_series, label='Price', color='green', lw=1.5)
            ax.plot(middle_band, label="Middle Band", color='blue', alpha=0.8)
            ax.plot(upper_band, label="Upper Band", color='red', alpha=0.8)
            ax.plot(lower_band, label="Lower Band", color='orange', alpha=0.8)

            # Plot buy and sell signals for Bollinger Bands
            for i, signal in enumerate(bollinger_signals):
                if signal == "Buy":
                    ax.scatter(i, prices_series[i], color='green', marker='^', label='Buy Signal' if i == 0 else "", alpha=1)
                elif signal == "Sell":
                    ax.scatter(i, prices_series[i], color='red', marker='v', label='Sell Signal' if i == 0 else "", alpha=1)

            # Set plot details for Bollinger Bands
            ax.set_title('Bollinger Bands Strategy', fontsize=12)
            ax.set_xlabel('Time', fontsize=10)
            ax.set_ylabel('Price ($)', fontsize=10)
            ax.grid(True)
            ax.legend(fontsize=8)

            # Layout adjustment
            plt.tight_layout()

            # Display the figure in Streamlit
            st.pyplot(fig)
            plt.close(fig)

        # Update Investment Info in Sidebar
        st.sidebar.write(f"Initial Investment: ${initial_investment}")
        st.sidebar.write(f"Final Portfolio Value: ${st.session_state['final_value']:.2f}")
        st.sidebar.write("Trade History:")
        st.sidebar.dataframe(st.session_state['trade_history'])


# Live update simulation based on refresh interval
while True:
    update_dashboard()
    time.sleep(refresh_interval)
