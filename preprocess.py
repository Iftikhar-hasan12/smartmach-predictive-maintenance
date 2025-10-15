import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# Register custom metrics at top level (outside functions)
try:
    import tensorflow as tf
    @tf.keras.utils.register_keras_serializable()
    def mse(y_true, y_pred):
        return tf.reduce_mean(tf.square(y_true - y_pred))

    @tf.keras.utils.register_keras_serializable()
    def mae(y_true, y_pred):
        return tf.reduce_mean(tf.abs(y_true - y_pred))
except ImportError:
    # Fallback if TensorFlow not available
    st.warning("TensorFlow not available - custom metrics not registered")

def load_data():
    """Load train and test data"""
    try:
        train_df = pd.read_csv("data/train_data.csv")
        test_df = pd.read_csv("data/test_data.csv")
        return train_df, test_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please make sure data files exist in the data/ folder")
        return None, None

def load_model(model_path):
    """Load the trained LSTM model with custom objects"""
    try:
        from tensorflow.keras.models import load_model as keras_load_model
        import tensorflow as tf
        
        # Re-register custom metrics inside function to ensure they're available
        @tf.keras.utils.register_keras_serializable()
        def mse(y_true, y_pred):
            return tf.reduce_mean(tf.square(y_true - y_pred))

        @tf.keras.utils.register_keras_serializable()
        def mae(y_true, y_pred):
            return tf.reduce_mean(tf.abs(y_true - y_pred))
            
        custom_objects = {'mse': mse, 'mae': mae}
        model = keras_load_model(model_path, custom_objects=custom_objects)
        st.success("✅ TensorFlow model loaded successfully!")
        return model
    except Exception as e:
        st.error(f"❌ TensorFlow model loading failed: {str(e)}")
        st.info("Running in demo mode with simulated predictions")
        return None

def scale_data(train_df, test_df):
    """Scale the data using MinMaxScaler"""
    if train_df is None or test_df is None:
        return None, None
        
    try:
        feature_cols = [col for col in train_df.columns if col not in ['unit_number', 'time_in_cycles', 'RUL']]
        
        scaler = MinMaxScaler()
        scaler.fit(train_df[feature_cols])
        
        train_df[feature_cols] = scaler.transform(train_df[feature_cols])
        test_df[feature_cols] = scaler.transform(test_df[feature_cols])
        
        return train_df, test_df
    except Exception as e:
        st.error(f"Error scaling data: {str(e)}")
        return train_df, test_df

def make_sequences(group, seq_length=50):
    """Create sequences from grouped data"""
    try:
        data = group.drop(['unit_number', 'time_in_cycles', 'RUL'], axis=1).values
        sequences, labels = [], []
        rul = group['RUL'].values
        
        for i in range(len(data) - seq_length + 1):
            seq = data[i:i+seq_length]
            label = rul[i+seq_length-1]
            sequences.append(seq)
            labels.append(label)
        
        return np.array(sequences), np.array(labels)
    except Exception as e:
        st.error(f"Error creating sequences: {str(e)}")
        return np.array([]), np.array([])

def create_dataset(df, seq_length=50):
    """Create dataset from dataframe"""
    try:
        X, y = [], []
        groups = df.groupby('unit_number')
        
        for _, group in groups:
            X_seq, y_seq = make_sequences(group, seq_length)
            if len(X_seq) > 0:
                X.extend(X_seq)
                y.extend(y_seq)
        
        return np.array(X), np.array(y)
    except Exception as e:
        st.error(f"Error creating dataset: {str(e)}")
        return np.array([]), np.array([])
