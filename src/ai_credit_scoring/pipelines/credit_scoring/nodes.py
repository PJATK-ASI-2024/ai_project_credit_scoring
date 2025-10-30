"""
This is a boilerplate pipeline 'credit_scoring'
generated using Kedro 1.0.0
"""
import pandas as pd

def load_data(data: pd.DataFrame) -> pd.DataFrame:
    return data

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.dropna()
    return data
