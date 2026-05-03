import joblib
import pandas as pd
import numpy as np

loaded = joblib.load("app/ml/kmeans_pipeline.pkl")

kmeans = loaded["model"]
scaler = loaded["scaler"]
fill_values = loaded["fill_values"]
num_cols = loaded["num_cols"]
binary_cols = loaded["binary_cols"]

def predict_cluster_service(payload: dict):
    
    
    df = pd.DataFrame([payload])

    for col in binary_cols:
        df[col] = df[col].astype(int)

    df[num_cols] = df[num_cols].fillna(fill_values)

    df_scaled = scaler.transform(df[num_cols])

    df_final = np.concatenate([df_scaled, df[binary_cols].values], axis=1)
    

    cluster = kmeans.predict(df_final)[0]

    return int(cluster)