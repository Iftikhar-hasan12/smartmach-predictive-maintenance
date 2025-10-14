import streamlit as st
from feature.health_monitor import predict_engine_health
from animation import show_loading_animation 
from feature.graph import graph 
from feature.single_eng_report import generate_and_download_report







def show_single_eng(engine_id, test_df, model, processor, seq_length=50):
    """Display single engine health report"""
    
    
    
    show_loading_animation("single", engine_id=engine_id)
    pred_rul, actual_rul, health_details = predict_engine_health(
        engine_id, test_df, model, processor, seq_length
    )

    if pred_rul is None:
        st.error(f"❌ Engine {engine_id} - Not enough data for prediction")
        return




    # Main metrics
    st.subheader(f"Engine {engine_id} - Health Report")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔮 Predicted RUL", f"{pred_rul} cycles")
    with col2:
        st.metric("📊 Actual RUL", f"{actual_rul} cycles")
    with col3:
        st.metric("❤️ Overall Health", f"{health_details['overall_health']}%")
    with col4:
        st.metric("📈 Status", health_details['health_status'])

    # Health components
    st.subheader("Health Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⏱️ RUL Health", f"{health_details['rul_health']}%")
    with col2:
        st.metric("📡 Sensor Health", f"{health_details['sensor_health']}%")
    with col3:
        st.metric("🚨 Critical Sensors", len(health_details['critical_sensors']))
    with col4:
        st.metric("⚠️ Warning Sensors", len(health_details['warning_sensors']))

    # Show critical sensors warning if any
    if health_details['critical_sensors']:
        st.error(f"🚨 **Critical Sensors Alert:** {', '.join(health_details['critical_sensors'])}")
    
    if health_details['warning_sensors']:
        st.warning(f"⚠️ **Warning Sensors:** {', '.join(health_details['warning_sensors'])}")


    
    # Sensor status table - Show ALL sensors with better formatting
    st.subheader("Complete Sensor Status (Today)")
    
    # Create a more detailed sensor table
    sensor_data = []
    for sensor_name, info in health_details['sensor_status_today'].items():
        sensor_data.append({
            'Sensor Name': sensor_name,
            'Current Value': f"{info['value']} {info.get('unit', '')}",
            'Status': info['status'],
            'Anomaly Level': f"{info['anomaly_level']}%",
            'Current Score': f"{info['score']}%"
        })
    
    if sensor_data:
        # Display all sensors in a table with better formatting
        st.dataframe(
            sensor_data,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Also show sensor count summary
        total_sensors = len(sensor_data)
        ok_sensors = len([s for s in sensor_data if '✅' in s['Status']])
        warning_sensors = len([s for s in sensor_data if '⚠️' in s['Status']])
        critical_sensors = len([s for s in sensor_data if '🚨' in s['Status']])
        
        st.write(f"**Sensor Summary:** Total: {total_sensors} | ✅ OK: {ok_sensors} | ⚠️ Warning: {warning_sensors} | 🚨 Critical: {critical_sensors}")
        
        # Show detailed sensor breakdown in expanders
        with st.expander("Detailed Sensor Breakdown by Status"):
            # Critical Sensors
            if critical_sensors > 0:
                st.subheader("🚨 Critical Sensors")
                critical_data = [s for s in sensor_data if '🚨' in s['Status']]
                st.dataframe(critical_data, use_container_width=True, hide_index=True)
            
            # Warning Sensors
            if warning_sensors > 0:
                st.subheader("⚠️ Warning Sensors")
                warning_data = [s for s in sensor_data if '⚠️' in s['Status']]
                st.dataframe(warning_data, use_container_width=True, hide_index=True)
            
            # OK Sensors
            if ok_sensors > 0:
                st.subheader("✅ Normal Sensors")
                ok_data = [s for s in sensor_data if '✅' in s['Status']]
                st.dataframe(ok_data, use_container_width=True, hide_index=True)
    else:
        st.warning("No sensor data available for this engine.")

   

    # Sensor Visualization Dashboard
    with st.expander("Sensor Visualization Dashboard"):
        graph(engine_id, test_df, processor, health_details, seq_length=50)

    # ✅ ADD THIS SECTION FOR PDF REPORT GENERATION
      # ✅ FIXED: Simple report button that doesn't cause rerun issues
      
      
       # Additional engine information
    with st.expander("Engine Technical Details"):
        st.write(f"**Analysis Window:** Last {seq_length} cycles")
        st.write(f"**Total Sensors Monitored:** {len(health_details['sensor_status_today'])}")
        st.write(f"**Health Calculation:** 60% RUL Health + 40% Sensor Health")
      
    with st.expander("Sensor Analysis Technical Details", expanded=False):
            st.markdown("""
           
            #### 1. Anomaly Level Calculation
            
            **Anomaly Level = Average deviation from normal ranges over 50 cycles**
            - current_value = Actual sensor reading (scaled 0-1)

            - current_score = Health percentage (100 - anomaly)

            For each cycle:
            - If value < low_threshold: `Anomaly = (low_threshold - value) / low_threshold × 100`
            - If value > high_threshold: `Anomaly = (value - high_threshold) / high_threshold × 100`  
            - If within range: `Anomaly = |value - ideal| / (high - low) × 50`

            **Final Anomaly = Average of all 50 cycles**

            #### 2. Current Sensor Score Formula
            **Current Score = 100 - Anomaly Level**

            - **100%** = Perfectly normal (0% anomaly)
            - **80%** = Minor deviations (20% anomaly) 
            - **50%** = Moderate issues (50% anomaly)
            - **0%** = Critical failure (100% anomaly)

            #### 3. Sensor Status Classification
            **Based on CURRENT VALUE only:**
            - **✅ OK**: `low_threshold ≤ current_value ≤ high_threshold`
            - **⚠️ LOW**: `current_value < low_threshold` 
            - **🚨 HIGH**: `current_value > high_threshold`

            #### 4. Sensor Health Calculation
            **Overall Sensor Health = Average(All Current Scores)**
            """)  
    with st.expander("📄 Generate Report", expanded=False):
      generate_and_download_report(engine_id, test_df, processor, pred_rul, actual_rul, health_details)


# ---------------------------------------------------------------
# ✅ EXTRA FUNCTION: Return all calculated values for Cost Optimizer
# ---------------------------------------------------------------

def get_engine_health_values(engine_id, test_df, model, processor, seq_length=50):
    """
    Returns key calculated values for a specific engine.
    Used by cost_optimizer to fetch latest health data.

    Returns:
        dict: {
            'predicted_rul': int,
            'sensor_health': float,
            'warning_sensors': int,
            'critical_sensors': int,
            'good_sensors': int,
            'anomaly_level': float,
            'current_score': float
        }
    """

    try:
        pred_rul, actual_rul, health_details = predict_engine_health(
            engine_id, test_df, model, processor, seq_length
        )

        if pred_rul is None or health_details is None:
            return None

        # Sensor breakdown
        sensor_status_today = health_details['sensor_status_today']
        warning_count = len(health_details['warning_sensors'])
        critical_count = len(health_details['critical_sensors'])
        total_sensors = len(sensor_status_today)
        good_count = total_sensors - (warning_count + critical_count)

        # Calculate average anomaly level and score
        anomaly_levels = [s['anomaly_level'] for s in sensor_status_today.values()]
        scores = [s['score'] for s in sensor_status_today.values()]
        avg_anomaly = round(sum(anomaly_levels) / len(anomaly_levels), 2) if anomaly_levels else 0
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0

        return {
            'predicted_rul': pred_rul,
            'sensor_health': health_details['sensor_health'],
            'warning_sensors': warning_count,
            'critical_sensors': critical_count,
            'good_sensors': good_count,
            'anomaly_level': avg_anomaly,
            'sensor_health': avg_score
        }

    except Exception as e:
        print(f"Error in get_engine_health_values: {str(e)}")
        return None
