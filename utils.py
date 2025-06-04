import os
import time
import requests
import matplotlib.pyplot as plt
import pandas as pd
import ta
import mplfinance as mpf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
MODEL_URL = os.getenv('MODEL_URL')

# Function to fetch historical price data from Binance API
def fetch_historical_data(symbol='BTCUSDT', interval='1m', limit=60):
    url = f'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Convert timestamps to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    # Convert numeric columns to float
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    return df

# Function to calculate technical indicators
def calculate_indicators(df):
    # Calculate Moving Averages
    df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['EMA_50'] = ta.trend.ema_indicator(df['close'], window=50)
    
    # Calculate RSI
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    
    # Calculate MACD
    macd = ta.trend.macd(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd['MACD']
    df['MACD_Signal'] = macd['MACD_SIGNAL']
    df['MACD_Hist'] = macd['MACD_DIFF']
    
    # Calculate Candlestick Patterns
    df['Hammer'] = ta.trend.hammer(df['open'], df['high'], df['low'], df['close'])
    df['Engulfing'] = ta.trend.engulfing(df['open'], df['high'], df['low'], df['close'])
    
    return df

# Function to plot and save the chart
def plot_chart(df):
    # Create a subplot for the main chart and indicators
    fig, axes = mpf.plot(df, type='candle', style='yahoo', volume=True, addplot=[
        mpf.make_addplot(df['SMA_20'], color='b'),
        mpf.make_addplot(df['EMA_50'], color='r'),
        mpf.make_addplot(df['MACD'], panel=1, color='g', ylabel='MACD'),
        mpf.make_addplot(df['MACD_Signal'], panel=1, color='orange', ylabel='MACD Signal'),
        mpf.make_addplot(df['MACD_Hist'], type='bar', panel=1, color='dimgray', ylabel='MACD Hist'),
        mpf.make_addplot(df['RSI'], panel=2, type='line', ylabel='RSI', ylim=(0, 100)),
        mpf.make_addplot([30] * len(df), panel=2, type='line', color='green', linestyle='--', linewidth=1),
        mpf.make_addplot([70] * len(df), panel=2, type='line', color='red', linestyle='--', linewidth=1)
    ], returnfig=True)
    
    # Annotate Hammer patterns
    hammer_indices = df[df['Hammer'] == 1].index
    for idx in hammer_indices:
        axes[0].annotate('Hammer', xy=(idx, df.loc[idx, 'high']), xytext=(idx, df.loc[idx, 'high'] + 1000),
                         arrowprops=dict(facecolor='blue', shrink=0.05))
    
    # Annotate Engulfing patterns
    engulfing_indices = df[df['Engulfing'] == 1].index
    for idx in engulfing_indices:
        axes[0].annotate('Engulfing', xy=(idx, df.loc[idx, 'high']), xytext=(idx, df.loc[idx, 'high'] + 1000),
                         arrowprops=dict(facecolor='red', shrink=0.05))
    
    # Save the chart
    filename = f'screenshot_{int(time.time())}.png'
    plt.savefig(filename)
    plt.close(fig)
    print(f"Chart saved as {filename}")
    return filename
