
# INVESTLY - Data Engineering App

## Description
**INVESTLY** is a data engineering application that integrates with the Binance API to fetch cryptocurrency data, showcase 3 trading strategies, and simulate a trading process. The application provides:
- Real-time cryptocurrency data via the Binance API.
- 3 trading strategies with buy/sell signals visualized in plots.
- A trading simulator where users can add an initial investment and see simulated trading results.

## Table of Contents
1. [Pulling the project and running the containers](#pulling-the-project-and-running-the-containers)
2. [Fetching the data from Binance API](#fetching-the-data-from-binance-api)
3. [Setting up the Docker architecture](#setting-up-the-docker-architecture)
    - 3.1 [Version](#version)
    - 3.2 [Networks](#networks)
    - 3.3 [Services](#services)
    - 3.4 [Volumes](#volumes)
4. [Getting data from Nifi](#getting-data-from-nifi)
5. [Handling data in Apache Spark](#handling-data-in-apache-spark)
    - 5.1 [Creating the Spark Conf](#creating-the-spark-conf)
    - 5.2 [Processing the data](#processing-the-data)
6. [Trading strategies & Dashboard Development with Streamlit](#trading-strategies--dashboard-development-with-streamlit)
    - 6.1 [Double Moving Averages](#double-moving-averages)
    - 6.2 [RSI](#rsi)
    - 6.3 [Bollingers Bands](#bollingers-bands)
    - 6.4 [Simulating trading process](#simulating-trading-process)

---

## 1. Pulling the project and running the containers

### Prerequisites
- Docker Engine installed on your system
- Git installed on your system

### Instructions
1. Clone the project repository:
    ```bash
    git clone -b final_version https://github.com/MohamedOuhami/cryptoCurrency_Trading_Plateform.git
    ```

2. Navigate into the project directory:
    ```bash
    cd cryptoCurrency_Trading_Plateform
    ```

3. Open the project in your preferred IDE (e.g., VSCode, Nvim).

4. Review the project’s architecture.

5. Modify the `.env` file to customize environment variables (like passwords).

6. Ensure that Docker Engine is running and start the services:
    ```bash
    docker-compose up -d
    ```

Now, all services should be running.

---

## 2. Fetching the data from Binance API

- The data is fetched from the Binance API, which provides cryptocurrency prices in US dollars.
- For example, to get the price of Bitcoin (BTC) in US dollars, use the following endpoint:
    ```bash
    https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT
    ```

- The response will look like this:
    ```json
    {
      "symbol": "BTCUSDT",
      "price": "98785.52000000"
    }
    ```

- The project retrieves data for 10 different coins and processes it accordingly.

---

## 3. Setting up the Docker architecture

The application uses Docker to containerize several services. Below is the breakdown of the architecture:

### 3.1 Version
- Docker Compose version: `3.8`.

### 3.2 Networks
- A custom network named `binance_app_network` is used to ensure that all services can communicate securely.

### 3.3 Services
1. **Zookeeper**: A configuration management service.
2. **NiFi Registry**: For version control of data flows.
3. **Spark Components**: For ETL processes.
4. **NiFi**: For real-time data integration.
5. **ElasticSearch**: For storing and analyzing data.

### 3.4 Volumes
- Volumes are used for persisting data outside the containers, preventing data loss when containers are stopped.

---

## 4. Getting data from Nifi

The workflow in this project includes 7 NiFi processors for retrieving, processing, and storing cryptocurrency data in ElasticSearch. Steps include:
- Fetching coin data from the Binance API.
- Parsing the data and storing it in an ElasticSearch index.

---

## 5. Handling data in Apache Spark

### 5.1 Creating the Spark Conf
- Apache Spark is used for handling the data transformation and analysis.

### 5.2 Processing the data
- The data fetched from the Binance API is processed using Apache Spark for further analysis and strategy implementation.

---

## 6. Trading strategies & Dashboard Development with Streamlit

The dashboard is developed using Streamlit and includes 3 different trading strategies:

### 6.1 Double Moving Averages
- Buy/sell signals are generated based on the crossing of two moving averages.

### 6.2 RSI (Relative Strength Index)
- Buy/sell signals are generated based on RSI values indicating overbought/oversold conditions.

### 6.3 Bollinger Bands
- Signals are generated based on the relationship between the price and Bollinger Bands.

### 6.4 Simulating trading process
- The app simulates a trading process, where users can input an initial investment and see how it would perform using the trading strategies.

---

## Conclusion

INVESTLY is a powerful tool for anyone interested in cryptocurrency trading. With its combination of real-time data, advanced trading strategies, and a trading simulator, it provides a comprehensive platform for testing and developing trading strategies.

---

### Notes
- Ensure that all dependencies are installed and configured correctly.
- You may need to adjust your system's resources to run the containers efficiently.

Enjoy using INVESTLY!
