import streamlit as st
import plotly.graph_objects as go
import numpy as np

def graph(engine_id, test_df, processor, health_details, seq_length=50):
    """Create enhanced sensor visualization using pre-calculated sensor data with threshold lines"""
    try:
        engine_data = test_df[test_df['unit_number'] == engine_id].tail(seq_length)
        if engine_data.empty:
            st.warning(f"No data found for Engine {engine_id}")
            return

        st.subheader(f"Engine {engine_id} - Sensor Visualization (Based on AI Health Report)")

        # ✅ Use pre-calculated health data
        sensor_status_today = health_details.get("sensor_status_today", {})
        if not sensor_status_today:
            st.warning("No sensor health data found.")
            return

        # ✅ Plot each sensor
        for sensor_name, info in sensor_status_today.items():
            value = info["value"]
            unit = info.get("unit", "")
            status = info["status"]
            anomaly = info["anomaly_level"]
            score = info["score"]

            # Color coding for visual clarity
            if "🚨" in status:
                color = "red"
            elif "⚠️" in status:
                color = "orange"
            else:
                color = "green"

            # Identify sensor key
            if sensor_name in processor.sensor_mapping.values():
                sensor_key = [k for k, v in processor.sensor_mapping.items() if v == sensor_name][0]
                values = engine_data[sensor_key].values

                # Convert to realistic values
                realistic_vals = [processor.get_realistic_value(sensor_name, v)[0] for v in values]
                time_labels = [f"Cycle {i+1}" for i in range(len(realistic_vals))]

                # ✅ Get threshold (scaled → realistic)
                low_scaled, high_scaled = processor.sensor_thresholds.get(sensor_key, (0.1, 0.9))
                min_thr, _ = processor.get_realistic_value(sensor_name, low_scaled)
                max_thr, _ = processor.get_realistic_value(sensor_name, high_scaled)

                # ✅ Create figure with thresholds
                fig = go.Figure()

                # Sensor data line
                fig.add_trace(go.Scatter(
                    x=time_labels,
                    y=realistic_vals,
                    mode='lines+markers',
                    line=dict(color=color, width=3),
                    name=f"{sensor_name} Value"
                ))

                # Min threshold line
                fig.add_hline(
                    y=min_thr,
                    line=dict(color='blue', dash='dot'),
                    annotation_text=f"Min Threshold ({min_thr}{unit})",
                    annotation_position="bottom right"
                )

                # Max threshold line
                fig.add_hline(
                    y=max_thr,
                    line=dict(color='red', dash='dot'),
                    annotation_text=f"Max Threshold ({max_thr}{unit})",
                    annotation_position="top right"
                )

                # Layout & styling
                fig.update_layout(
                    title=f"{sensor_name} ({status}) | Current Score: {score}% | Anomaly: {anomaly}%",
                    title_font=dict(color=color, size=16),
                    xaxis_title="Cycle",
                    yaxis_title=f"Value ({unit})",
                    height=450,
                    margin=dict(l=50, r=50, t=80, b=50),
                    plot_bgcolor='rgba(245,245,245,0.8)',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")

        st.success("✅ Visualization synced with thresholds and AI Health Report successfully.")

    except Exception as e:
        st.error(f"Error creating synced sensor analysis: {str(e)}")
