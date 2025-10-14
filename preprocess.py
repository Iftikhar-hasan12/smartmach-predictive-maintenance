import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.metrics import MeanSquaredError, MeanAbsoluteError
import tensorflow as tf

# Register custom metrics
@tf.keras.utils.register_keras_serializable()
def mse(y_true, y_pred):
    return tf.reduce_mean(tf.square(y_true - y_pred))

@tf.keras.utils.register_keras_serializable()
def mae(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true - y_pred))
#----------------------------Model loading------------------------------
def load_data():
    """Load train and test data"""
    train_df = pd.read_csv("data/train_data.csv")
    test_df = pd.read_csv("data/test_data.csv")
    return train_df, test_df

def load_model(model_path):
    """Load model with graceful fallback for deployment"""
    try:
        from tensorflow.keras.models import load_model as keras_load_model
        import tensorflow as tf
        
        # Register custom metrics
        @tf.keras.utils.register_keras_serializable()
        def mse(y_true, y_pred):
            return tf.reduce_mean(tf.square(y_true - y_pred))

        @tf.keras.utils.register_keras_serializable()
        def mae(y_true, y_pred):
            return tf.reduce_mean(tf.abs(y_true - y_pred))
            
        custom_objects = {'mse': mse, 'mae': mae}
        return keras_load_model(model_path, custom_objects=custom_objects)
    except Exception as e:
        print(f"Model loading failed: {e}")
        # Return a dummy model or None
        return None
        #---------------------------------------------------

def scale_data(train_df, test_df):
    """Scale the data using MinMaxScaler"""
    feature_cols = [col for col in train_df.columns if col not in ['unit_number', 'time_in_cycles', 'RUL']]
    
    scaler = MinMaxScaler()
    scaler.fit(train_df[feature_cols])
    
    train_df[feature_cols] = scaler.transform(train_df[feature_cols])
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])
    
    return train_df, test_df

def make_sequences(group, seq_length=50):
    """Create sequences from grouped data"""
    data = group.drop(['unit_number', 'time_in_cycles', 'RUL'], axis=1).values
    sequences, labels = [], []
    rul = group['RUL'].values
    
    for i in range(len(data) - seq_length + 1):
        seq = data[i:i+seq_length]
        label = rul[i+seq_length-1]
        sequences.append(seq)
        labels.append(label)
    
    return np.array(sequences), np.array(labels)

def create_dataset(df, seq_length=50):
    """Create dataset from dataframe"""
    X, y = [], []
    groups = df.groupby('unit_number')
    
    for _, group in groups:
        X_seq, y_seq = make_sequences(group, seq_length)
        X.extend(X_seq)
        y.extend(y_seq)
    
    return np.array(X), np.array(y)
