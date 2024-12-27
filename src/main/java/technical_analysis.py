import sys  # Додадете го на врвот на скриптата
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


# Functions for indicators
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

def calculate_ema(data, window):
    return data['Close'].ewm(span=window, adjust=False).mean()

def calculate_macd(data):
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_rsi(data, window):
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_stochastic(data, k_window=14, d_window=3):
    lowest_low = data['Low'].rolling(window=k_window).min()
    highest_high = data['High'].rolling(window=k_window).max()
    k_line = 100 * ((data['Close'] - lowest_low) / (highest_high - lowest_low))
    d_line = k_line.rolling(window=d_window).mean()
    return k_line, d_line

def calculate_cci(data, window):
    tp = (data['High'] + data['Low'] + data['Close']) / 3
    sma = tp.rolling(window=window).mean()
    mad = tp.rolling(window=window).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    cci = (tp - sma) / (0.015 * mad)
    return cci

def calculate_bollinger_bands(data, window=20, num_std=2):
    sma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    bb_upper = sma + (num_std * std)
    bb_lower = sma - (num_std * std)
    return bb_upper, bb_lower


def calculate_atr(data, window):
    high = data['High']
    low = data['Low']
    close_prev = data['Close'].shift(1)
    true_range = np.maximum(high - low, np.maximum(abs(high - close_prev), abs(low - close_prev)))
    true_range = pd.Series(true_range)
    atr = true_range.rolling(window=window).mean()
    return atr

def calculate_obv(data):
    obv = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
    return obv


def determine_action(value, overbought=70, oversold=30):
    if value > overbought:
        return "Sell"
    elif value < oversold:
        return "Buy"
    else:
        return "Hold"

def generate_html_table(data, title, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    html_content = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                font-family: Arial, sans-serif;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f4f4f4;
                font-weight: bold;
            }}
            .buy {{ color: green; font-weight: bold; }}
            .sell {{ color: red; font-weight: bold; }}
            .hold {{ color: orange; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>Value</th>
                <th>Action</th>
            </tr>
    """
    for _, row in data.iterrows():
        action_class = row['Action'].lower()
        html_content += f"""
            <tr>
                <td>{row['Name']}</td>
                <td>{row['Value']:.2f}</td>
                <td class="{action_class}">{row['Action']}</td>
            </tr>
        """
    html_content += """
        </table>
    </body>
    </html>
    """
    html_file_path = os.path.join(output_path, f"{title.replace(' ', '_').lower()}.html")
    with open(html_file_path, 'w') as f:
        f.write(html_content)
    return html_file_path

def save_plot(data, issuer, plot_name, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    filepath = os.path.join(output_path, f"{plot_name}.png")
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath


# Main script
if __name__ == "__main__":
    issuer = sys.argv[1]
    csv_path = sys.argv[2]
    #output_path=sys.argv[3]
    output_path = os.path.join("src", "main", "resources", "static", f"{issuer}_tables")


    data = pd.read_csv(csv_path)
   # issuer = "AAPL"  # Example issuer
   # csv_path = "path/to/your/data.csv"  # Replace with your CSV file path
   # output_path = os.path.join("src", "main", "resources", "static")
    #output_path = os.path.join('src', 'main', 'resources', 'static', f'{issuer}_tables')


    # Load data
   # data = pd.read_csv(csv_path)


    if 'Issuer' not in data.columns or 'Close' not in data.columns or 'Date' not in data.columns:
        print("Missing required columns in CSV file")
        sys.exit(1)
    data = data[data['Issuer'] == issuer]
    if data.empty:
        print(f"No data found for issuer: {issuer}")
        sys.exit(1)

    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
    #data.dropna(subset=['Date'], inplace=True)
    data['Close'] = pd.to_numeric(data['Close'].replace({',': ''}, regex=True), errors='coerce')
    data.dropna(subset=['Close'], inplace=True)
    data['High'] = data['High'].replace({',': ''}, regex=True)
    data['High'] = pd.to_numeric(data['High'], errors='coerce')

    data['Low'] = data['Low'].replace({',': ''}, regex=True)
    data['Low'] = pd.to_numeric(data['Low'], errors='coerce')

    # Отстранете ги редовите со неконвертирани вредности
    data.dropna(subset=['Close', 'High', 'Low'], inplace=True)

    data.sort_values(by='Date', inplace=True)
    data.set_index('Date', inplace=True)




    #data['Date'] = pd.to_datetime(data['Date'])
    #data.set_index('Date', inplace=True)

    # Calculate indicators
    data['SMA_10'] = calculate_sma(data, 10)
    data['EMA_10'] = calculate_ema(data, 10)
    data['RSI'] = calculate_rsi(data, 14)
    data['K'], data['D'] = calculate_stochastic(data)
    data['CCI'] = calculate_cci(data, 20)

    data['MACD'], data['Signal_Line'] = calculate_macd(data)  # MACD и сигнална линија
    data['BB_Upper'], data['BB_Lower'] = calculate_bollinger_bands(data, 20)  # Bollinger опсези
    data['ATR'] = calculate_atr(data, 14)  # Average True Range
    data['OBV'] = calculate_obv(data)  # On-Balance Volume

    # Generate tables for different timeframes
    for period, label in [('1D', '1 Day'), ('1M', '1 Month'), ('1Y', '1 Year')]:
        max_date = data.index.max()
        print(f"Max date in data: {max_date}")

        if period.endswith('D'):  # Денови
            start_date = max_date - pd.Timedelta(days=int(period[:-1]))
            filtered_data = data[(data.index > start_date) & (data.index <= max_date)]
        elif period.endswith('M'):  # Месеци
            start_date = max_date - pd.DateOffset(months=int(period[:-1]))
            filtered_data = data[(data.index > start_date) & (data.index <= max_date)]
        elif period.endswith('Y'):  # Години
            start_date = max_date - pd.DateOffset(years=int(period[:-1]))
            filtered_data = data[(data.index > start_date) & (data.index <= max_date)]

        print(f"Filtered data for {label}: Start date = {start_date}, Records found = {len(filtered_data)}")

        if filtered_data.empty:
            print(f"No data found for period: {label}")
            continue

        print(f"Filtered data for {label}: {filtered_data.index.min()} to {filtered_data.index.max()}")

        indicators = [
            {"Name": "Simple Moving Average (10)", "Value": filtered_data['SMA_10'].iloc[-1]},
            {"Name": "Exponential Moving Average (10)", "Value": filtered_data['EMA_10'].iloc[-1]},
            {"Name": "Relative Strength Index (14)", "Value": filtered_data['RSI'].iloc[-1]},
            {"Name": "Stochastic %K", "Value": filtered_data['K'].iloc[-1]},
            {"Name": "Commodity Channel Index (20)", "Value": filtered_data['CCI'].iloc[-1]},
            {"Name": "Moving Average Convergence Divergence (MACD)", "Value": filtered_data['MACD'].iloc[-1]},
            {"Name": "Bollinger Bands Upper (20)", "Value": filtered_data['BB_Upper'].iloc[-1]},
            {"Name": "Bollinger Bands Lower (20)", "Value": filtered_data['BB_Lower'].iloc[-1]},
            {"Name": "Average True Range (14)", "Value": filtered_data['ATR'].iloc[-1]},
            {"Name": "On-Balance Volume (OBV)", "Value": filtered_data['OBV'].iloc[-1]}
        ]

        for indicator in indicators:
            indicator["Action"] = determine_action(indicator["Value"])

        indicators_df = pd.DataFrame(indicators)
        title = f"Technical Indicators and Moving Averages - {label}"
        generate_html_table(indicators_df, title, output_path)


    data['SMA_20'] = calculate_sma(data, 20)
    data['EMA_20'] = calculate_ema(data, 20)

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['SMA_20'], label='SMA (20)', color='red')
    plt.plot(data.index, data['EMA_20'], label='EMA (20)', color='green')
    plt.title(f'SMA and EMA for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'sma_ema_plot', output_path)

    data['MACD'], data['Signal'] = calculate_macd(data)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['MACD'], label='MACD', color='purple')
    plt.plot(data.index, data['Signal'], label='Signal Line', color='orange')
    plt.title(f'MACD for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'macd_plot', output_path)

    data['RSI'] = calculate_rsi(data, 14)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['RSI'], label='RSI', color='brown')
    plt.axhline(70, linestyle='--', color='red', label='Overbought')
    plt.axhline(30, linestyle='--', color='green', label='Oversold')
    plt.title(f'RSI for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'rsi_plot', output_path)

    print("sma_ema_plot.png")
    print("macd_plot.png")
    print("rsi_plot.png")



    # Print all generated HTML files
    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".html"):
                print(file)






'''
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

def calculate_ema(data, window):
    return data['Close'].ewm(span=window, adjust=False).mean()

def calculate_macd(data):
    short_ema = data['Close'].ewm(span=12, adjust=False).mean()
    long_ema = data['Close'].ewm(span=26, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_rsi(data, window):
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def save_plot(data, issuer, plot_name, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    filepath = os.path.join(output_path, f"{plot_name}.png")
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath

if __name__ == "__main__":
    issuer = sys.argv[1]
    csv_path = sys.argv[2]

    data = pd.read_csv(csv_path)

    if 'Issuer' not in data.columns or 'Close' not in data.columns or 'Date' not in data.columns:
        print("Missing required columns in CSV file")
        sys.exit(1)

    data = data[data['Issuer'] == issuer]

    if data.empty:
        print(f"No data found for issuer: {issuer}")
        sys.exit(1)

    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
    data.dropna(subset=['Date'], inplace=True)
    data['Close'] = pd.to_numeric(data['Close'].replace({',': ''}, regex=True), errors='coerce')
    data.dropna(subset=['Close'], inplace=True)

    data.sort_values(by='Date', inplace=True)
    data.set_index('Date', inplace=True)

    output_path = os.path.join('src', 'main', 'resources', 'static', f'{issuer}_plots')

    data['SMA_20'] = calculate_sma(data, 20)
    data['EMA_20'] = calculate_ema(data, 20)

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['SMA_20'], label='SMA (20)', color='red')
    plt.plot(data.index, data['EMA_20'], label='EMA (20)', color='green')
    plt.title(f'SMA and EMA for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'sma_ema_plot', output_path)

    data['MACD'], data['Signal'] = calculate_macd(data)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['MACD'], label='MACD', color='purple')
    plt.plot(data.index, data['Signal'], label='Signal Line', color='orange')
    plt.title(f'MACD for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'macd_plot', output_path)

    data['RSI'] = calculate_rsi(data, 14)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['RSI'], label='RSI', color='brown')
    plt.axhline(70, linestyle='--', color='red', label='Overbought')
    plt.axhline(30, linestyle='--', color='green', label='Oversold')
    plt.title(f'RSI for {issuer}')
    plt.legend()
    save_plot(data, issuer, 'rsi_plot', output_path)

    print("sma_ema_plot.png")
    print("macd_plot.png")
    print("rsi_plot.png")
'''