import numpy as np

class HealthScoreCalculator:
    def __init__(self, processor):
        self.processor = processor

    def calculate_sensor_health(self, sensor_history, current_sensors):
        sensor_status_today = {}
        critical_sensors = []
        warning_sensors = []
        sensor_health_scores = []

        for sensor, display_name in self.processor.sensor_mapping.items():
            if sensor not in self.processor.sensor_thresholds:
                continue

            low, high = self.processor.sensor_thresholds[sensor]
            current_value = current_sensors.get(sensor, None)
            historical_values = sensor_history.get(sensor, [])

            if current_value is None or len(historical_values) == 0:
                continue

            # Calculate anomaly based on ENTIRE 50-cycle history
            anomaly_scores = []
            for value in historical_values:
                if value < low:
                    # How far below low threshold
                    anomaly = (low - value) / low * 100
                elif value > high:
                    # How far above high threshold
                    anomaly = (value - high) / high * 100
                else:
                    # Within threshold, but calculate distance from ideal (middle)
                    ideal = (low + high) / 2
                    anomaly = abs(value - ideal) / (high - low) * 50  # Max 50% for within-range deviation
                anomaly_scores.append(anomaly)

            # Overall anomaly level (average of all 50 cycles)
            overall_anomaly_level = np.mean(anomaly_scores)
            
            # Sensor health score (100 - overall anomaly)
            score = max(0, 100 - overall_anomaly_level)

            # Current status (based only on current value)
            if low <= current_value <= high:
                current_status = "✅ OK"
            elif current_value < low:
                current_status = "⚠️ LOW"
                warning_sensors.append(display_name)
            else:
                current_status = "🚨 HIGH" 
                critical_sensors.append(display_name)

            # Get realistic value for display
            realistic_value, unit = self.processor.get_realistic_value(display_name, current_value)
            
            sensor_status_today[display_name] = {
                "value": realistic_value,
                "unit": unit,
                "status": current_status,  # Current status only
                "anomaly_level": round(overall_anomaly_level, 2),  # Based on 50 cycles
                "score": round(score, 2),  # Based on 50 cycles
                "history_analysis": f"Based on {len(historical_values)} cycles"  # For transparency
            }
            sensor_health_scores.append(score)

        avg_sensor_health = round(np.mean(sensor_health_scores), 2) if sensor_health_scores else 100.0
        return avg_sensor_health, sensor_status_today, critical_sensors, warning_sensors

#-----------------------------------Called from function no -2-------------------------        

    def calculate_overall_health_score(self, predicted_rul, sensor_history, current_sensors):
        # RUL health scoring (unchanged)
        if predicted_rul > 150:
            rul_health = 100
        elif predicted_rul > 50:
            rul_health = 70
        elif predicted_rul > 20:
            rul_health = 40
        elif predicted_rul > 1:
            rul_health = 5
        else:
            rul_health = 0

        # Sensor health (now based on 50-cycle analysis)
        sensor_health, sensor_status_today, critical_sensors, warning_sensors = \
            self.calculate_sensor_health(sensor_history, current_sensors)

        # Overall health (weighted avg)
        overall_health = round((0.6 * rul_health + 0.4 * sensor_health), 2)

        if overall_health >= 65:
            health_status = "✅ GOOD"
        elif overall_health >= 41:
            health_status = "⚠️ WARNING"
        else:
            health_status = "🚨 CRITICAL"

        return overall_health, {
            "overall_health": overall_health,
            "health_status": health_status,
            "rul_health": rul_health,
            "sensor_health": sensor_health,
            "sensor_status_today": sensor_status_today,
            "critical_sensors": critical_sensors,
            "warning_sensors": warning_sensors
        }


# --------------------------------Called from the all engine Function-no_01 -----------
def predict_engine_health(engine_id, test_df, model, processor, seq_length=50):
    """Predict engine health with RUL and sensor analysis"""
    test_groups = test_df.groupby('unit_number')

    if engine_id not in test_df['unit_number'].unique():
        return None, None, None

    engine_data = test_groups.get_group(engine_id)

    if len(engine_data) < seq_length:
        return None, None, None

    last_window = engine_data.tail(seq_length)
    X_last = last_window.drop(['unit_number', 'time_in_cycles', 'RUL'], axis=1).values
    X_last = X_last.reshape(1, seq_length, X_last.shape[1])

    y_pred = model.predict(X_last, verbose=0)
    predicted_rul = int(round(y_pred[0][0]))
    actual_rul = int(last_window['RUL'].iloc[-1])

    current_sensors = {s: last_window[s].iloc[-1] for s in processor.sensor_mapping.keys()}
    sensor_history = {s: last_window[s].values for s in processor.sensor_mapping.keys()}

    health_calculator = HealthScoreCalculator(processor)
    overall_health, health_details = health_calculator.calculate_overall_health_score(
        predicted_rul, sensor_history, current_sensors
    )

    return predicted_rul, actual_rul, health_details