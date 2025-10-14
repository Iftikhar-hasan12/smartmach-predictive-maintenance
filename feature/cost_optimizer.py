
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def cost_optimizer(engine_id, engine_data):
    # Elegant Header
    # st.markdown("""
    # <div style='background:linear-gradient(90deg, #5A60FF 0%, #6C63FF 100%);
    #             padding:1px; border-radius:16px; box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-bottom:25px;'>
    #     <h1 style='color:white; margin:0; text-align:center;'>💰 AI Maintenance Cost Optimizer</h1>
    #     <p style='color:#e0e0e0; text-align:center; margin-top:8px;'>Smart Decisions • Lower Costs • AI Precision</p>
    # </div>
    # """, unsafe_allow_html=True)

    # Engine Info 
    st.markdown(f"""
    <div style='background:#f9f9fb; padding:15px 25px; border-radius:12px; border-left:6px solid #5A60FF; margin-bottom:25px;
                box-shadow:0 2px 5px rgba(0,0,0,0.05);'>
        <h3 style='margin:0; color:#333;'>Cost Optimizer</h3>
        <p style='margin:6px 0 0 0; color:#555;'>Analyzing data for <strong>Engine ID: {engine_id}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------
    # Load Model
    # ---------------------------------
    try:
        with open("model/cost_model.pkl", "rb") as f:
            cost_model = pickle.load(f)
    except Exception as e:
        st.error(f"❌ Model not found or load error: {e}")
        return

    # ---------------------------------
    # Extract Data
    # ---------------------------------
    predicted_rul = engine_data.get('predicted_rul', 0)
    warning_count = engine_data.get('warning_sensors', 0)
    critical_count = engine_data.get('critical_sensors', 0)
    good_count = engine_data.get('good_sensors', 0)
    sensor_health = engine_data.get('sensor_health', 0)
    anomaly_level = engine_data.get('anomaly_level', 0)

    # ---------------------------------
    # Engine Health Summary
    # ---------------------------------
    st.markdown("### Engine Health Overview")
    col1, col2,  col3 = st.columns(3)

    col1.metric("🔮 Predicted RUL", f"{predicted_rul} days")
    col2.metric("❤️ Sensor Score", f"{sensor_health}%", "Good" if sensor_health > 70 else "Weak")
    #col3.metric("🚨 Critical Sensors", critical_count)
    col3.metric("📈 Anomaly Level", f"{anomaly_level}%")

    # ---------------------------------
    # Sensor Breakdown
    # ---------------------------------
    st.markdown("### Sensor Status")
    col_a, col_b, col_c = st.columns(3)

    col_a.markdown(f"<h4 style='font-size:22px;'>✅ Good Sensors: <b>{good_count}</b></h4>", unsafe_allow_html=True)
    col_b.markdown(f"<h4 style='font-size:22px;'>⚠️ Warning Sensors: <b>{warning_count}</b></h4>", unsafe_allow_html=True)
    col_c.markdown(f"<h4 style='font-size:22px;'>🚨 Critical Sensors: <b>{critical_count}</b></h4>", unsafe_allow_html=True)




    # ---------------------------------
    # Build 4 Scenarios
    # ---------------------------------
    # st.markdown("### Maintenance Scenarios")
    scenarios = pd.DataFrame({
        "repair_day": ["before_10_days", "today", "end_cycle", "after_10_days"],
        "warning_sensors": [warning_count]*4,
        "critical_sensors": [critical_count]*4,
        "good_sensors": [good_count]*4,
        "predicted_rul": [predicted_rul]*4,
        "sensor_health": [sensor_health]*4,
        "anomaly_level": [anomaly_level]*4
    })

    scenarios["repair_day"] = scenarios["repair_day"].map({
        "before_10_days": -10,
        "today": predicted_rul,
        "end_cycle": 0,
        "after_10_days": 10
    })

    # ---------------------------------
    # Predict Costs
    # ---------------------------------
    X = scenarios[[
        "repair_day", "warning_sensors", "critical_sensors",
        "good_sensors", "predicted_rul", "sensor_health", "anomaly_level"
    ]]
    scenarios["predicted_cost"] = cost_model.predict(X)

    penalty_per_day = 200000
    scenarios["final_cost"] = scenarios["predicted_cost"]

    for i, row in scenarios.iterrows():
        if row["repair_day"] == 0:
            scenarios.loc[i, "final_cost"] += 1 * penalty_per_day
        elif row["repair_day"] == 10:
            scenarios.loc[i, "final_cost"] += 11 * penalty_per_day

  # ---------------------------------
    # Cost Table (Updated with Repair Time)
    # ---------------------------------
    st.markdown("### Cost Summary")

    display = scenarios.copy()
    display["Scenario"] = ["🟢 Preventive", "🟡 Current", "🟠 End-of-Life", "🔴 Emergency"]
    display["Repair Time"] = ["Before 10 Days", f"Today, {predicted_rul} days before", "End of Cycle", "After 10 Days"]
    display["Penalty"] = display["final_cost"] - display["predicted_cost"]

    show = display[["Scenario", "Repair Time", "predicted_cost", "Penalty", "final_cost"]].rename(
        columns={
            "predicted_cost": "Base Cost (৳)",
            "Penalty": "Downtime Cost (৳)",
            "final_cost": "Total Cost (৳)"
        }
    )

    # Format values
    show["Base Cost (৳)"] = show["Base Cost (৳)"].apply(lambda x: f"৳{x:,.0f}")
    show["Downtime Cost (৳)"] = show["Downtime Cost (৳)"].apply(lambda x: f"৳{x:,.0f}")
    show["Total Cost (৳)"] = show["Total Cost (৳)"].apply(lambda x: f"৳{x:,.0f}")

    # Display the updated table
    st.dataframe(show, use_container_width=True, hide_index=True)

    # ---------------------------------
    # Best Case
    # ---------------------------------
    best_idx = scenarios["final_cost"].idxmin()
    best = scenarios.loc[best_idx]
    savings = scenarios["final_cost"].max() - best["final_cost"]

    st.markdown(f"""
    <div style='background:#EAF8EA; padding:20px; border-radius:10px; border-left:6px solid #28a745; 
                box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
        <h3 style='margin-top:0;'> Optimal Strategy</h3>
        <p>Recommended: <strong>{show.iloc[best_idx]["Scenario"]}</strong></p>
        <p> Estimated Total Cost: <strong>৳{best["final_cost"]:,.0f}</strong></p>
        <p> Potential Savings: <strong>৳{savings:,.0f}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------
    #  Visualization
    # ---------------------------------
    st.markdown("###  Cost Visualization")
    labels = show["Scenario"]
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "bar"}]])

    fig.add_trace(
        go.Pie(labels=labels, values=scenarios["final_cost"], hole=0.45, 
               marker=dict(colors=["#28a745","#ffc107","#fd7e14","#dc3545"])), row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=labels, y=scenarios["final_cost"], 
               marker_color=["#28a745","#ffc107","#fd7e14","#dc3545"],
               text=scenarios["final_cost"].apply(lambda x: f"৳{x/100000:.1f}L"), textposition="outside"),
        row=1, col=2
    )

    fig.update_layout(height=520, showlegend=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

  
