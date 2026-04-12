import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

FEATURE_COLS = ["value", "rate_of_change", "rolling_std", "rolling_mean"]


def create_sequences(data, seq_length):
    n_features = data.shape[1] if data.ndim == 2 else 1
    sequences = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i : i + seq_length])
    tensor = torch.tensor(np.array(sequences), dtype=torch.float32)
    if tensor.ndim == 2:
        tensor = tensor.unsqueeze(2)
    return tensor


def split_data(df):
    n = len(df)
    train_end = int(n * config.TRAIN_RATIO)
    val_end = int(n * (config.TRAIN_RATIO + config.VAL_RATIO))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]


def get_data_loaders(file_path, seq_length=None, batch_size=None):
    seq_length = seq_length or config.SEQ_LENGTH
    batch_size = batch_size or config.BATCH_SIZE

    df = pd.read_csv(file_path, index_col="timestamp", parse_dates=True)

    if "rate_of_change" not in df.columns:
        from generate_data import add_engineered_features
        df = add_engineered_features(df)

    scaler = StandardScaler()
    available_features = [c for c in FEATURE_COLS if c in df.columns]
    df[available_features] = scaler.fit_transform(df[available_features])

    train_df, val_df, test_df = split_data(df)

    # Train: only normal data
    train_normal = train_df[~train_df["is_anomaly"]] if "is_anomaly" in train_df.columns else train_df
    train_values = train_normal[available_features].values
    train_seqs = create_sequences(train_values, seq_length)
    train_dataset = torch.utils.data.TensorDataset(train_seqs, train_seqs)
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=min(os.cpu_count() or 1, 4), persistent_workers=True,
    )

    # Val: only normal data (for threshold computation)
    val_normal = val_df[~val_df["is_anomaly"]] if "is_anomaly" in val_df.columns else val_df
    val_values = val_normal[available_features].values
    val_seqs = create_sequences(val_values, seq_length)
    val_dataset = torch.utils.data.TensorDataset(val_seqs, val_seqs)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size * 4, num_workers=0)

    # Test: all data (for precision/recall/F1)
    test_values = test_df[available_features].values
    test_seqs = create_sequences(test_values, seq_length)
    test_labels = test_df["is_anomaly"].values[seq_length:] if "is_anomaly" in test_df.columns else None
    test_dataset = torch.utils.data.TensorDataset(test_seqs)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size * 4, num_workers=0)

    return {
        "train_loader": train_loader,
        "val_loader": val_loader,
        "test_loader": test_loader,
        "test_labels": test_labels,
        "scaler": scaler,
        "full_df": df,
        "n_features": len(available_features),
    }
