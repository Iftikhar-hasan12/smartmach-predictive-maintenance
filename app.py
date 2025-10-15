import streamlit as st
from preprocess import load_data, scale_data, load_model
from feature.all_eng import show_all_eng
from feature.single_eng import show_single_eng
from feature.cost_optimizer import cost_optimizer
from feature.trend_forecast import show_trend_forecasting
from feature.single_eng import get_engine_health_values 

# ✅ Configuration
st.set_page_config(
    page_title="SmartMach: AI-Powered Predictive Maintenance System",
    page_icon="smartmach_logo.png",  # <-- your 64x64 PNG image (place it in the same folder)
    layout="wide"
)

# ✅ Sidebar Branding
st.sidebar.image("smartmach_logo.png", width=64)
st.sidebar.title("🤖 SmartMach Dashboard")
st.sidebar.caption("AI-Powered Predictive Maintenance System")
st.sidebar.markdown("---")

# ✅ Feature Selection
selected_feat = st.sidebar.radio("Select Feature", [ "All Engine Conditions", "Specific Engine", "Cost Optimizer", "Root Cause Analysis", "Trend Forecasting" ])

# -------------------------------Model & Dataset Loading-------------------------
if 'model' not in st.session_state or 'test_df' not in st.session_state:
    try:
        with st.spinner("🔄 Loading AI model and data..."):
            st.session_state.model = load_model("model/model.h5")
            st.session_state.train_df, st.session_state.test_df = load_data()
            st.session_state.train_df, st.session_state.test_df = scale_data(
                st.session_state.train_df, st.session_state.test_df
            )
        st.sidebar.success("Model and data loaded successfully!")
    except FileNotFoundError as e:
        st.error(f"❌ File not found: {str(e)}")
        st.info("Please check if these files exist:")
        st.info("- model/model.h5")
        st.info("- data/train_data.csv") 
        st.info("- data/test_data.csv")
        # Don't stop the app, allow other features to work
        st.session_state.model = None
        st.session_state.test_df = None
    except Exception as e:
        st.error(f"❌ Error loading model: {str(e)}")
        st.session_state.model = None
        st.session_state.test_df = None

# After model loading in session_state
if st.session_state.model is None:
    st.sidebar.warning("🤖 AI Model: Demo Mode (Using simulated predictions)")
    # You can add simulated predictions here
else:
    st.sidebar.success("🤖 AI Model: Loaded (TensorFlow Active)")

# -----------------------------------------Sensor to Readable Name mapping------------
sensor_thresholds = {
    'sensor_2': (0.1, 0.9), 'sensor_3': (0.1, 0.8), 'sensor_4': (0.2, 0.7),
    'sensor_6': (0.1, 0.85), 'sensor_7': (0.05, 0.8), 'sensor_8': (0.05, 0.8),
    'sensor_9': (0.05, 0.8), 'sensor_11': (0.1, 0.9), 'sensor_12': (0.1, 0.85),
    'sensor_13': (0.1, 0.9), 'sensor_14': (0.1, 0.9), 'sensor_15': (0.1, 0.9),
    'sensor_17': (0.1, 0.85), 'sensor_20': (0.1, 0.9), 'sensor_21': (0.1, 0.9)
}

sensor_mapping = {
    'sensor_2': 'Temperature', 'sensor_3': 'Pressure', 'sensor_4': 'RPM',
    'sensor_6': 'Fuel Flow', 'sensor_7': 'Vibration X', 'sensor_8': 'Vibration Y',
    'sensor_9': 'Vibration Z', 'sensor_11': 'Oil Temp', 'sensor_12': 'Oil Pressure',
    'sensor_13': 'Exhaust Temp', 'sensor_14': 'Compressor Temp', 'sensor_15': 'Fan Speed',
    'sensor_17': 'Throttle Position', 'sensor_20': 'Fuel Temp', 'sensor_21': 'Engine Load'
}

# Realistic value mapping for display
realistic_value_mapper = {
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
# ---------------------------------Create a object for the sensor mapping -----------------------
class DummyProcessor:
    def __init__(self, thresholds, mapping, realistic_mapper):
        self.sensor_thresholds = thresholds
        self.sensor_mapping = mapping
        self.realistic_mapper = realistic_mapper
    
    def get_realistic_value(self, sensor_name, scaled_value):
        """Convert scaled value (0-1) to realistic industrial value"""
        if sensor_name in self.realistic_mapper:
            mapper = self.realistic_mapper[sensor_name]
            realistic_value = scaled_value * (mapper['max'] - mapper['min']) + mapper['min']
            return round(realistic_value, 2), mapper['unit']
        return scaled_value, ""

# Initialize processor with ALL mappings
processor = DummyProcessor(sensor_thresholds, sensor_mapping, realistic_value_mapper)

# Main content
st.title("SmartMach: AI-Powered Predictive Maintenance System")
#st.markdown("### AI-Powered Predictive Maintenance & Analytics")


with st.sidebar.expander("🔧 System Status", expanded=False):
    if 'test_df' in st.session_state and st.session_state.test_df is not None:
        st.success(f"✅ Data: {st.session_state.test_df.shape[0]} rows, {st.session_state.test_df.shape[1]} cols")
        available_engines = st.session_state.test_df['unit_number'].unique()
        st.info(f"🚀 Engines: {len(available_engines)} total")
    else:
        st.error("❌ Data not loaded")
    
    if 'model' in st.session_state and st.session_state.model is not None:
        st.success("🤖 AI Model: Loaded")
    else:
        st.error("🤖 AI Model: Not loaded")

# Feature routing with proper error handling
if selected_feat == "All Engine Conditions":
    if st.session_state.test_df is not None and st.session_state.model is not None:
        show_all_eng(st.session_state.test_df, st.session_state.model, processor)
    else:
        st.error("❌ Data or model not loaded. Please check the system status in sidebar.")
        
elif selected_feat == "Specific Engine":
    if st.session_state.test_df is not None and st.session_state.model is not None:
        available_engines = st.session_state.test_df['unit_number'].unique()
        engine_id = st.slider("Select Engine ID:", 
                             min_value=int(min(available_engines)), 
                             max_value=int(max(available_engines)), 
                             value=int(min(available_engines)))
        
        if st.button("Analyze Engine Health", type="primary"):
            show_single_eng(engine_id, st.session_state.test_df, st.session_state.model, processor)
    else:
        st.error("❌ Data or model not loaded. Please check the system status in sidebar.")
        
elif selected_feat == "Cost Optimizer":
    if st.session_state.test_df is not None and st.session_state.model is not None:
    

        available_engines = st.session_state.test_df['unit_number'].unique()
        engine_id = st.slider("Select Engine ID:", 
                             min_value=int(min(available_engines)), 
                             max_value=int(max(available_engines)), 
                             value=int(min(available_engines)))

        if st.button("Optimize Maintenance Costs", type="primary"):
            # Automatically fetch health data before running cost optimizer
            with st.spinner("🔍 Collecting engine health data..."):
                engine_data = get_engine_health_values(
                    engine_id, st.session_state.test_df,
                    st.session_state.model, processor
                )

            if engine_data is None:
                st.warning("⚠️ Please analyze this engine first in the 'Specific Engine' tab.")
            else:
                st.success("✅ Engine health data fetched successfully!")
                # st.json(engine_data)

                # Now call the optimizer
                cost_optimizer(engine_id, engine_data)

    else:
        st.error("❌ Data or model not loaded. Please check the system status in sidebar.")


        
elif selected_feat == "Root Cause Analysis":
    if st.session_state.test_df is not None:
        available_engines = st.session_state.test_df['unit_number'].unique()
        engine_id = st.slider("Select Engine ID for Analysis:", 
                             min_value=int(min(available_engines)), 
                             max_value=int(max(available_engines)), 
                             value=int(min(available_engines)))
        
        if st.button("Analyze Root Causes", type="primary"):
            try:
                from feature.root_cause_analyzer import show_root_cause_analysis
                show_root_cause_analysis(engine_id, st.session_state.test_df, processor)
            except ImportError as e:
                st.error(f"❌ Missing dependency: {str(e)}")
                st.info("Please install required packages: pip install scikit-learn plotly")
            except Exception as e:
                st.error(f"❌ Error in root cause analysis: {str(e)}")
    else:
        st.error("❌ Data not loaded. Please check the system status in sidebar.")
        
elif selected_feat == "Trend Forecasting":
    if st.session_state.test_df is not None:
        available_engines = st.session_state.test_df['unit_number'].unique()
        engine_id = st.slider("Select Engine ID:", 
                              min_value=int(min(available_engines)), 
                              max_value=int(max(available_engines)), 
                              value=int(min(available_engines)))
        try:
            from feature.trend_forecast import show_trend_forecasting
            show_trend_forecasting(engine_id, st.session_state.test_df, processor)
        except Exception as e:
            st.error(f"❌ Error loading trend forecasting: {str(e)}")
    else:
        st.error("❌ Data not loaded. Please check the system status in sidebar.")






# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>⚙️ © 2025 SmartMach | Powered by AI & Machine Learning | All Rights Reserved</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# # Quick installation guide in sidebar
# with st.sidebar.expander("📦 Installation Guide", expanded=False):
#     st.markdown("""
#     **If features don't work:**
#     ```bash
#     pip install scikit-learn plotly pandas numpy streamlit tensorflow
#     ```
    
#     **Required files:**
#     - `model/model.h5`
#     - `data/train_data.csv`
#     - `data/test_data.csv`
#     """)
