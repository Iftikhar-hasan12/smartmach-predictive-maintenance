import streamlit as st
from feature.health_monitor import predict_engine_health
from animation import show_loading_animation
from feature.generatereport_all_eng import generate_fleet_report, create_csv_report
from datetime import datetime












# -------------------------------Function no_01------------------

def show_all_eng(test_df, model, processor, seq_length=50):
    """Display all engines health overview with 3-stage classification"""
    
    
    
    st.subheader("All Engines Health Overview")
    show_loading_animation("all")
    
    engine_health_scores = {}
    engine_details = {}

    # Calculate health for all engines------- 
    for engine_id in test_df['unit_number'].unique():
        # Hit the request to the health_monitor.py----------------------------------------
        pred_rul, actual_rul, health_details = predict_engine_health(
            engine_id, test_df, model, processor, seq_length
        )
        
        if pred_rul is not None:
            engine_health_scores[engine_id] = health_details['overall_health']
            engine_details[engine_id] = {
                'pred_rul': pred_rul,
                'actual_rul': actual_rul,
                'health_status': health_details['health_status'],
                'critical_sensors': len(health_details['critical_sensors']),
                'warning_sensors': len(health_details['warning_sensors'])
            }

    # Display health scores
    if engine_health_scores:
        # Separate engines by health status
        critical_engines = {eid: score for eid, score in engine_health_scores.items() if score < 41}
        warning_engines = {eid: score for eid, score in engine_health_scores.items() if 41 <= score < 65}
        good_engines = {eid: score for eid, score in engine_health_scores.items() if score >= 65}
        
        # 1. CRITICAL ENGINES TABLE
        if critical_engines:
            st.markdown("---")
            st.error("🚨 **CRITICAL ALERT: Engines Requiring Immediate Attention**")
            
            critical_data = []
            for eid, score in sorted(critical_engines.items()):
                details = engine_details[eid]
                critical_data.append({
                    'Engine ID': eid,
                    'Health Score': f"{score}%",
                    'Predicted RUL': details['pred_rul'],
                    'Actual RUL': details['actual_rul'],
                    'Critical Sensors': details['critical_sensors'],
                    'Warning Sensors': details['warning_sensors'],
                    'Status': '🚨 CRITICAL'
                })
            
            st.dataframe(
                critical_data,
                use_container_width=True,
                height=min(300, len(critical_data) * 35 + 40)
            )
        
        # 2. WARNING ENGINES TABLE
        if warning_engines:
            st.markdown("---")
            st.warning("⚠️ **WARNING: Engines Requiring Monitoring**")
            
            warning_data = []
            for eid, score in sorted(warning_engines.items()):
                details = engine_details[eid]
                warning_data.append({
                    'Engine ID': eid,
                    'Health Score': f"{score}%",
                    'Predicted RUL': details['pred_rul'],
                    'Actual RUL': details['actual_rul'],
                    'Critical Sensors': details['critical_sensors'],
                    'Warning Sensors': details['warning_sensors'],
                    'Status': '⚠️ WARNING'
                })
            
            st.dataframe(
                warning_data,
                use_container_width=True,
                height=min(300, len(warning_data) * 35 + 40)
            )
        
        # 3. GOOD ENGINES TABLE
        if good_engines:
            st.markdown("---")
            st.success("✅ **GOOD: Engines in Healthy Condition**")
            
            good_data = []
            for eid, score in sorted(good_engines.items()):
                details = engine_details[eid]
                good_data.append({
                    'Engine ID': eid,
                    'Health Score': f"{score}%",
                    'Predicted RUL': details['pred_rul'],
                    'Actual RUL': details['actual_rul'],
                    'Critical Sensors': details['critical_sensors'],
                    'Warning Sensors': details['warning_sensors'],
                    'Status': '✅ GOOD'
                })
            
            st.dataframe(
                good_data,
                use_container_width=True,
                height=min(400, len(good_data) * 35 + 40)
            )
        
        # 4. COMPLETE ENGINE HEALTH REPORT (Optional - with filters)
        st.markdown("---")
        st.subheader("Complete Engine Health Report (Filterable)")
        
        # Add filter options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            show_all = st.checkbox("Show All", value=True)
        with col2:
            show_critical = st.checkbox("Show Critical", value=True)
        with col3:
            show_warning = st.checkbox("Show Warning", value=True)
        with col4:
            show_good = st.checkbox("Show Good", value=True)
        
        # Filter data based on selection
        filtered_data = []
        for eid, score in sorted(engine_health_scores.items()):
            details = engine_details[eid]
            
            # Determine engine category
            is_critical = score < 41
            is_warning = 41 <= score < 65
            is_good = score >= 65
            
            # Apply filters
            if not show_all:
                if is_critical and not show_critical:
                    continue
                if is_warning and not show_warning:
                    continue
                if is_good and not show_good:
                    continue
                
            filtered_data.append({
                'Engine ID': eid,
                'Health Score': f"{score}%",
                'Status': details['health_status'],
                'Predicted RUL': details['pred_rul'],
                'Actual RUL': details['actual_rul'],
                'Critical Sensors': details['critical_sensors'],
                'Warning Sensors': details['warning_sensors']
            })
        
        if filtered_data:
            st.dataframe(
                filtered_data,
                use_container_width=True,
                height=min(600, len(filtered_data) * 35 + 40)
            )
            
            # Show summary
            total_engines = len(filtered_data)
            critical_count = len([d for d in filtered_data if '🚨' in d['Status']])
            warning_count = len([d for d in filtered_data if '⚠️' in d['Status']])
            good_count = len([d for d in filtered_data if '✅' in d['Status']])
            
            st.write(f"**Summary:** Total: {total_engines} | ✅ Good: {good_count} | ⚠️ Warning: {warning_count} | 🚨 Critical: {critical_count}")
        else:
            st.info("No engines match the selected filters")
            
        # Overall Fleet Health Summary
        st.markdown("---")
        st.subheader("Fleet Health Summary")
        
        total_fleet = len(engine_health_scores)
        fleet_critical = len(critical_engines)
        fleet_warning = len(warning_engines)
        fleet_good = len(good_engines)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Engines", total_fleet)
        with col2:
            st.metric("✅ Good", f"{fleet_good} ({fleet_good/total_fleet*100:.1f}%)")
        with col3:
            st.metric("⚠️ Warning", f"{fleet_warning} ({fleet_warning/total_fleet*100:.1f}%)")
        with col4:
            st.metric("🚨 Critical", f"{fleet_critical} ({fleet_critical/total_fleet*100:.1f}%)")
            
    else:
        st.error("No engine data available for analysis")


        st.markdown("---")
        
        
        
    with st.expander("How Health Scores Are Calculated", expanded=False):
        st.markdown("""
        **Health Score = 60% RUL Health + 40% Sensor Health**

        #### RUL Health (60%)
        - **100%** = 150+ cycles remaining
        - **70%** = 50-150 cycles  
        - **40%** = 20-50 cycles
        - **5%** = 1-20 cycles
        - **0%** = 0 cycles

        #### Sensor Health (40%)
        - Each sensor scored 0-100% based on 50-cycle history
        - If value < low_threshold → "⚠️ LOW"
        - If value > high_threshold → "🚨 HIGH"
        - If within range → "✅ OK"

        #### Final Status (Health Score) 
        - **✅ GOOD** = 65-100% (Healthy)
        - **⚠️ WARNING** = 41-64% (Monitor)  
        - **🚨 CRITICAL** = 0-40% (Urgent)
        """)
    st.subheader("📥 Download Report")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            with st.spinner("Generating professional PDF report..."):
                pdf_buffer = generate_fleet_report(engine_health_scores, engine_details, test_df, processor)
                if pdf_buffer:
                    st.success("PDF report generated successfully!")
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"fleet_health_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    with col2:
        if st.button("📊 Generate CSV Report", use_container_width=True):
            with st.spinner("Generating CSV report..."):
                csv_buffer = create_csv_report(engine_health_scores, engine_details)
                if csv_buffer:
                    st.success("CSV report generated successfully!")
                    st.download_button(
                        label="⬇️ Download CSV Data",
                        data=csv_buffer,
                        file_name=f"fleet_health_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                     )