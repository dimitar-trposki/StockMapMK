import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Load data from CSV file
data = pd.read_csv('stock_data.csv', encoding='utf-8')
data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')

# Filter data for a specific issuer (e.g., ADIN)
issuer_data = data[data['Issuer'] == 'ADIN']

# Prepare data
issuer_data = issuer_data.sort_values(by='Date')
issuer_data['Close'] = issuer_data['Close'].str.replace(',', '').astype(float)

# Normalize the data using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(issuer_data[['Close']])

# Create sequences for LSTM input
sequence_length = 60
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data, sequence_length)

# Split data into training and validation sets
train_size = int(len(X) * 0.7)
X_train, X_val = X[:train_size], X[train_size:]
y_train, y_val = y[:train_size], y[train_size:]

# Reshape data for LSTM input
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_val = np.reshape(X_val, (X_val.shape[0], X_val.shape[1], 1))

# Build the LSTM model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    tf.keras.layers.LSTM(units=50, return_sequences=False),
    tf.keras.layers.Dense(units=25),
    tf.keras.layers.Dense(units=1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = model.fit(X_train, y_train, batch_size=32, epochs=50, validation_data=(X_val, y_val))

# Evaluate the model
train_predictions = model.predict(X_train)
val_predictions = model.predict(X_val)

# Rescale predictions back to original values
train_predictions = scaler.inverse_transform(train_predictions)
y_train_rescaled = scaler.inverse_transform(y_train.reshape(-1, 1))

val_predictions = scaler.inverse_transform(val_predictions)
y_val_rescaled = scaler.inverse_transform(y_val.reshape(-1, 1))

# Calculate RMSE for validation data
rmse = np.sqrt(mean_squared_error(y_val_rescaled, val_predictions))
print(f'Validation RMSE: {rmse}')

# Plot results
plt.figure(figsize=(14, 5))
plt.plot(issuer_data['Date'][-len(y_val_rescaled):], y_val_rescaled, color='blue', label='Actual Prices')
plt.plot(issuer_data['Date'][-len(val_predictions):], val_predictions, color='red', label='Predicted Prices')
plt.title('Actual vs Predicted Stock Prices')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Save the trained model
model.save('lstm_stock_model.h5')

# Forecast future prices
def forecast_next_n_days(model, data, n_days, scaler):
    last_sequence = data[-sequence_length:]
    forecasted_prices = []

    for _ in range(n_days):
        prediction = model.predict(last_sequence[np.newaxis, :, :])
        forecasted_prices.append(prediction[0, 0])
        last_sequence = np.append(last_sequence[1:], prediction[0, 0]).reshape(-1, 1)

    return scaler.inverse_transform(np.array(forecasted_prices).reshape(-1, 1))

# Forecast the next 30 days
forecasted_prices = forecast_next_n_days(model, scaled_data, 30, scaler)
print('Forecasted Prices for the Next 30 Days:', forecasted_prices)


# Save the forecasted prices to a CSV file
forecasted_prices_df = pd.DataFrame(forecasted_prices, columns=['Forecasted Price'])
forecasted_prices_df.index.name = 'Day'
forecasted_prices_df.to_csv('/content/forecasted_prices.csv', encoding='utf-8')

forecasted_prices_df.head()
