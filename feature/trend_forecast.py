import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# 🔹 Simple value converter
# -------------------------------
def convert_to_realistic_value(sensor_name, scaled_value):
    """Convert scaled value to realistic industrial value"""
    realistic_mapper = {
        'Temperature': {'unit': '°C', 'min': 20, 'max': 120},
        'Pressure': {'unit': 'PSI', 'min': 0, 'max': 100},
        'RPM': {'unit': 'RPM', 'min': 0, 'max': 3000},
        'Fuel Flow': {'unit': 'L/min', 'min': 0, 'max': 50},
        'Vibration X': {'unit': 'mm/s', 'min': 0, 'max': 10},
        'Vibration Y': {'unit': 'mm/s', 'min': 0, 'max': 10},
        'Vibration Z': {'unit': 'mm/s', 'min': 0, 'max': 10},
        'Oil Temp': {'unit': '°C', 'min': 60, 'max': 120},
        'Oil Pressure': {'unit': 'PSI', 'min': 20, 'max': 80},
        'Exhaust Temp': {'unit': '°C', 'min': 300, 'max': 600},
        'Compressor Temp': {'unit': '°C', 'min': 100, 'max': 300},
        'Fan Speed': {'unit': 'RPM', 'min': 0, 'max': 2000},
        'Throttle Position': {'unit': '%', 'min': 0, 'max': 100},
        'Fuel Temp': {'unit': '°C', 'min': 15, 'max': 50},
        'Engine Load': {'unit': '%', 'min': 0, 'max': 100}
    }
    
    if sensor_name in realistic_mapper:
        mapper = realistic_mapper[sensor_name]
        realistic_value = scaled_value * (mapper['max'] - mapper['min']) + mapper['min']
        return realistic_value, mapper['unit']
    return scaled_value, ""

# -------------------------------
# 🔹 Sequence generator
# -------------------------------
def make_sequences(series, seq_len=50):
    X, y = [], []
    for i in range(len(series) - seq_len):
        X.append(series[i:i+seq_len])
        y.append(series[i+seq_len])
    
    # Check if we have any sequences before reshaping
    if len(X) == 0:
        return np.array([]), np.array([])
    
    # Convert to numpy arrays and reshape
    X = np.array(X)
    y = np.array(y)
    
    # Only reshape if we have sequences
    if len(X.shape) == 2:  # Only reshape if it's 2D (samples, seq_len)
        X = X[:, :, np.newaxis]  # Shape: (samples, seq_len, 1)
    
    return X, y

# -------------------------------
# 🔹 Train and forecast RNN
# -------------------------------
def train_predict_rnn(engine_data, sensor_col, seq_len=50, forecast_days=10):
    series = engine_data[sensor_col].values.astype(float)

    # We need more data than seq_len to create sequences
    if len(series) <= seq_len:
        st.warning(f"Not enough data to create sequences! Need more than {seq_len} points, got {len(series)}")
        return []

    # Scale
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.reshape(-1, 1)).flatten()

    X, y = make_sequences(scaled, seq_len)
    
    # Check if sequences were created
    if len(X) == 0:
        st.warning(f"Cannot create sequences with {len(series)} points and sequence length {seq_len}")
        return []

    # Model
    model = Sequential([
        SimpleRNN(32, input_shape=(seq_len, 1)),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # Train
    model.fit(X, y, epochs=20, batch_size=16, verbose=0)

    # Forecast using the last available sequence
    last_seq = scaled[-seq_len:]
    future_preds_scaled = []
    temp_seq = last_seq.copy()

    for _ in range(forecast_days):
        x_input = temp_seq[-seq_len:].reshape(1, seq_len, 1)
        pred_scaled = model.predict(x_input, verbose=0)[0, 0]
        future_preds_scaled.append(pred_scaled)
        temp_seq = np.append(temp_seq, pred_scaled)

    # Convert to original scale
    future_preds = scaler.inverse_transform(
        np.array(future_preds_scaled).reshape(-1, 1)
    ).flatten()
    
    return future_preds

# -------------------------------
# 🔹 Trend & Alerts based on last 3 days
# -------------------------------
def get_trend_and_alerts(last_3, high=None, low=None):
    if len(last_3) < 3:
        return "Insufficient Data ➡️", False, False
        
    if last_3[2] > last_3[1] > last_3[0]:
        direction = "Increasing 📈"
    elif last_3[2] < last_3[1] < last_3[0]:
        direction = "Decreasing 📉"
    else:
        direction = "Stable ➡️"

    will_cross_high = high is not None and last_3[-1] > high
    will_cross_low = low is not None and last_3[-1] < low

    return direction, will_cross_high, will_cross_low

# -------------------------------
# 🔹 Plot last 50 + next 10 days
# -------------------------------
def plot_last50_next10(hist_realistic, future_realistic, sensor_name, unit, low=None, high=None):
    last_50 = hist_realistic[-50:]
    plt.figure(figsize=(10, 3))
    plt.plot(range(1, 51), last_50, label='Actual (Last 50)', color='blue')
    plt.plot(range(51, 61), future_realistic, label='Forecast (Next 10)', color='orange', marker='o')
    plt.axvline(x=50, color='gray', linestyle='--', label='Forecast Start')

    if high is not None:
        plt.axhline(y=high, color='red', linestyle=':', label='High Threshold')
    if low is not None:
        plt.axhline(y=low, color='orange', linestyle=':', label='Low Threshold')

    plt.title(f"{sensor_name} - Last 50 + Next 10 Days Forecast")
    plt.xlabel("Day")
    plt.ylabel(f"Sensor Value ({unit})")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(plt)
    plt.clf()

# -------------------------------
# 🔹 Main Streamlit Function with Sensor Selection
# -------------------------------
def show_trend_forecasting(engine_id, test_df, processor):
    st.header("RNN Trend Forecasting")
    
    # Filter engine data
    engine_data = test_df[test_df['unit_number'] == engine_id].reset_index(drop=True)
    
    if engine_data.empty:
        st.error(f"❌ No data found for Engine {engine_id}")
        return

    st.subheader("Sensor Selection")
    
    # Get available sensors from processor mapping
    available_sensors = list(processor.sensor_mapping.keys())
    
    # Create sensor selection dropdown with readable names
    selected_sensor = st.selectbox(
        "Select Sensor to Forecast:",
        available_sensors,
        format_func=lambda x: f"{processor.sensor_mapping[x]} ({x})",
        index=available_sensors.index('sensor_21')  # Default to Engine Load
    )

    if not selected_sensor:
        st.warning("Please select a sensor")
        return

    sensor_name = processor.sensor_mapping[selected_sensor]
    
    st.markdown(f"### Analyzing: {sensor_name} ({selected_sensor})")

    # Parameters
    history_days = 100  # Use 100 points for training
    seq_length = 50     # Use 50-point sequences
    forecast_days = 10
    
    # Check if we have enough data
    if len(engine_data) < history_days:
        st.warning(f"Not enough data for {sensor_name}. Need at least {history_days} points, got {len(engine_data)}")
        st.info(f"Available data points for Engine {engine_id}: {len(engine_data)}")
        return

    st.info(f"Using {history_days} data points with {seq_length}-day sequences for training")

    # Display engine info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Engine ID", engine_id)
    with col2:
        st.metric("Total Data Points", len(engine_data))
    with col3:
        st.metric("Selected Sensor", sensor_name)

    # Forecast
    try:
        with st.spinner(f"Training RNN and forecasting for {sensor_name}..."):
            future_preds = train_predict_rnn(
                engine_data.tail(history_days), 
                selected_sensor,
                seq_len=seq_length, 
                forecast_days=forecast_days
            )

        if len(future_preds) == 0:
            st.warning("Could not generate forecasts - not enough training data")
            return

        st.success("✅ Forecast generated successfully!")

        # Convert historical data to realistic values
        hist_scaled = engine_data[selected_sensor].tail(history_days).values
        hist_realistic = []
        for v in hist_scaled:
            realistic_val, unit = convert_to_realistic_value(sensor_name, float(v))
            hist_realistic.append(realistic_val)

        # Convert future predictions to realistic values
        future_realistic = []
        future_units = []
        for v in future_preds:
            realistic_val, unit = convert_to_realistic_value(sensor_name, float(v))
            future_realistic.append(realistic_val)
            future_units.append(unit)

        # Get the unit for display (use first one)
        display_unit = future_units[0] if future_units else ""

        # Convert thresholds to realistic values
        low_threshold_scaled = processor.sensor_thresholds[selected_sensor][0]
        high_threshold_scaled = processor.sensor_thresholds[selected_sensor][1]
        
        low_threshold_realistic, _ = convert_to_realistic_value(sensor_name, low_threshold_scaled)
        high_threshold_realistic, _ = convert_to_realistic_value(sensor_name, high_threshold_scaled)

        # Trend analysis based on last 3 historical points
        if len(hist_realistic) >= 3:
            last_3 = hist_realistic[-3:]
            direction, will_cross_high, will_cross_low = get_trend_and_alerts(
                last_3,
                high=high_threshold_realistic,
                low=low_threshold_realistic
            )

            # Display trend and alerts
            trend_col, alert_col = st.columns(2)
            with trend_col:
                st.metric("Current Trend", direction)
            
            with alert_col:
                if will_cross_high:
                    st.error(f"🚨 Approaching High Threshold!")
                elif will_cross_low:
                    st.warning(f"⚠️ Approaching Low Threshold!")
                else:
                    st.success("✅ Within Normal Range")

        # Display predictions in a nice table
        st.subheader("10-Day Forecast Details")
        
        pred_data = []
        for i, pred in enumerate(future_realistic, 1):
            status = "✅ Normal"
            if pred > high_threshold_realistic:
                status = "🚨 High"
            elif pred < low_threshold_realistic:
                status = "⚠️ Low"
                
            pred_data.append({
                "Day": i,
                "Predicted Value": f"{pred:.2f} {display_unit}",
                "Status": status
            })
        
        # Display as table
        st.table(pred_data)

        # Plot visualization
        st.subheader("Forecast Visualization")
        plot_last50_next10(
            hist_realistic, 
            future_realistic,
            sensor_name,
            display_unit,
            low=low_threshold_realistic,
            high=high_threshold_realistic
        )

        # Additional insights
        st.subheader("Insights")
        
        # Calculate some basic statistics
        avg_pred = np.mean(future_realistic)
        max_pred = np.max(future_realistic)
        min_pred = np.min(future_realistic)
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        with insight_col1:
            st.metric("Average Forecast", f"{avg_pred:.2f} {display_unit}")
        with insight_col2:
            st.metric("Maximum Forecast", f"{max_pred:.2f} {display_unit}")
        with insight_col3:
            st.metric("Minimum Forecast", f"{min_pred:.2f} {display_unit}")

    except Exception as e:
        st.error(f"❌ Error during forecasting: {str(e)}")
        st.info("Please try selecting a different sensor or engine.")