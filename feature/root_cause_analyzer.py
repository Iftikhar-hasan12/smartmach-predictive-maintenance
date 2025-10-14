# feature/root_cause_analyzer.py
import streamlit as st
import pandas as pd
import numpy as np
import shap
import plotly.express as px
import pickle

def show_root_cause_analysis(engine_id, test_df, processor):
    """Explain which sensors contribute most to RUL using RandomForest + SHAP"""
    try:
        # Load model
        with open("model/rf.pkl", "rb") as f:
            model = pickle.load(f)

        # Filter engine data
        engine_data = test_df[test_df['unit_number'] == engine_id].tail(1)
        if engine_data.empty:
            st.error(f"No data found for Engine {engine_id}")
            return

        # Prepare input (keep time_laps for prediction)
        X_input = engine_data.drop(columns=['unit_number', 'time_in_cycles', 'RUL'])
        feature_names = X_input.columns

        # Predict RUL
        predicted_rul = model.predict(X_input)[0]

        # ---- FEATURE IMPORTANCE (GLOBAL) ----
        importances = model.feature_importances_
        imp_df = pd.DataFrame({
            "Sensor": feature_names,
            "Importance": importances
        })

        # Remove 'time_laps' (keep for prediction but hide in chart)
        imp_df = imp_df[imp_df["Sensor"] != "time_laps"]

        # ✅ Apply human-friendly names using processor mapping
        imp_df["Display Name"] = imp_df["Sensor"].apply(
            lambda x: processor.sensor_mapping.get(x, x)
        )

        # Sort and select top 10
        imp_df = imp_df.sort_values(by="Importance", ascending=False).head(10)

        st.markdown(f"### Feature Importance of Engine {engine_id}")
        fig = px.bar(
            imp_df,
            x="Importance",
            y="Display Name",
            orientation="h",
            title="Top 10 Most Influential Factors on Remaining Useful Life (RUL)",
            color="Importance",
            color_continuous_scale="viridis"
        )
        fig.update_layout(yaxis_title="Feature", xaxis_title="Importance")
        st.plotly_chart(fig, use_container_width=True)

        # ---- SHAP ANALYSIS (LOCAL EXPLANATION) ----
        st.markdown("### SHAP-based Local Explanation for This Engine")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_input)

        # SHAP DataFrame
        shap_df = pd.DataFrame({
            "Sensor": feature_names,
            "SHAP Value": shap_values[0],
            "Current Value": X_input.values[0]
        })

        # Remove time_laps
        shap_df = shap_df[shap_df["Sensor"] != "time_laps"]

        # ✅ Apply sensor mapping for readable labels
        shap_df["Display Name"] = shap_df["Sensor"].apply(
            lambda x: processor.sensor_mapping.get(x, x)
        )

        shap_df = shap_df.sort_values(by="SHAP Value", ascending=False).head(10)

        fig2 = px.bar(
            shap_df,
            x="SHAP Value",
            y="Display Name",
            orientation="h",
            color="SHAP Value",
            color_continuous_scale="RdBu",
            # title=f"Top 10 Factors Affecting Engine {engine_id}'s Predicted RUL"
        )
        fig2.update_layout(yaxis_title="Feature", xaxis_title="SHAP Impact")
        st.plotly_chart(fig2, use_container_width=True)

        # Table
        st.dataframe(
            shap_df[["Display Name", "Current Value", "SHAP Value"]]
            .rename(columns={
                "Display Name": "Feature",
                "Current Value": "Current Value (scaled)",
                "SHAP Value": "SHAP Contribution"
            })
            .style.format({"Current Value (scaled)": "{:.3f}", "SHAP Contribution": "{:.3f}"}),
            use_container_width=True,
            hide_index=True,
            height=350
        )

        # Result summary
        # st.success(f"✅ Root cause analysis completed successfully for Engine {engine_id}!")
        # st.info(f"🔮 Predicted Remaining Useful Life (RUL): **{predicted_rul:.2f} cycles**")

    except Exception as e:
        st.error(f"Error in root cause analysis: {str(e)}")
        st.info("Make sure you have installed scikit-learn, shap, and plotly: pip install scikit-learn shap plotly")
