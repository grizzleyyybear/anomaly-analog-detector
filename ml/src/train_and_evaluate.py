import json
import logging
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
import config
from data_preprocessing import get_data_loaders, create_sequences
from model import LSTMAutoencoder

log = logging.getLogger(__name__)
torch.set_float32_matmul_precision("medium")


def compute_losses(model, loader, device):
    model.eval()
    losses = []
    with torch.no_grad():
        for batch in loader:
            seq = batch[0].to(device)
            output = model(seq)
            loss = torch.mean((seq - output) ** 2, dim=(1, 2))
            losses.extend(loss.cpu().numpy().tolist())
    return losses


def train_lstm():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    data_file = config.DATA_DIR / "sensor_data.csv"
    if not data_file.exists():
        from generate_data import generate_sensor_data
        generate_sensor_data()

    log.info("Loading data with train/val/test split")
    data = get_data_loaders(str(data_file), config.SEQ_LENGTH, config.BATCH_SIZE)
    train_loader = data["train_loader"]
    val_loader = data["val_loader"]
    test_loader = data["test_loader"]
    test_labels = data["test_labels"]
    n_features = data["n_features"]
    full_df = data["full_df"]

    log.info(f"Features: {n_features} | Train: {len(train_loader.dataset)} | Val: {len(val_loader.dataset)} | Test: {len(test_loader.dataset)}")

    model = LSTMAutoencoder(
        input_size=n_features,
        hidden_size=config.LSTM_HIDDEN_SIZE,
        seq_len=config.SEQ_LENGTH,
        learning_rate=config.LSTM_LR,
    )

    config.CHECKPOINT_DIR.mkdir(exist_ok=True)

    checkpoint_cb = ModelCheckpoint(
        dirpath=str(config.CHECKPOINT_DIR), filename="best-model", monitor="train_loss", mode="min",
    )
    early_stop_cb = EarlyStopping(monitor="train_loss", patience=3, verbose=True, mode="min")

    trainer = pl.Trainer(
        max_epochs=config.LSTM_EPOCHS,
        callbacks=[checkpoint_cb, early_stop_cb],
        log_every_n_steps=1,
        accelerator="auto",
    )

    log.info("Training LSTM autoencoder")
    trainer.fit(model, train_loader)
    log.info("Training complete")

    best_path = trainer.checkpoint_callback.best_model_path
    trained_model = LSTMAutoencoder.load_from_checkpoint(best_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    trained_model.to(device)
    trained_model.eval()

    # Dynamic threshold from validation set (normal data only)
    log.info("Computing threshold from validation set")
    val_losses = compute_losses(trained_model, val_loader, device)
    mean_loss = float(np.mean(val_losses))
    std_loss = float(np.std(val_losses))
    threshold = mean_loss + config.THRESHOLD_SIGMA * std_loss

    threshold_data = {
        "threshold": threshold,
        "mean_loss": mean_loss,
        "std_loss": std_loss,
        "sigma": config.THRESHOLD_SIGMA,
        "seq_length": config.SEQ_LENGTH,
        "n_features": n_features,
        "val_samples": len(val_losses),
    }
    with open(config.THRESHOLD_FILE, "w") as f:
        json.dump(threshold_data, f, indent=2)
    log.info(f"Threshold: {threshold:.6f} (mean={mean_loss:.6f}, σ={std_loss:.6f})")

    # Evaluate on test set with ground truth labels
    log.info("Evaluating on test set")
    test_losses = compute_losses(trained_model, test_loader, device)
    predicted_anomalies = [1 if l > threshold else 0 for l in test_losses]

    metrics = {"threshold": threshold, "test_samples": len(test_losses)}

    if test_labels is not None and len(test_labels) == len(predicted_anomalies):
        true_labels = test_labels.astype(int).tolist()
        precision = precision_score(true_labels, predicted_anomalies, zero_division=0)
        recall = recall_score(true_labels, predicted_anomalies, zero_division=0)
        f1 = f1_score(true_labels, predicted_anomalies, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(true_labels, predicted_anomalies, labels=[0, 1]).ravel()

        metrics.update({
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn),
        })

        log.info(f"Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
        log.info(f"TP={tp} FP={fp} TN={tn} FN={fn}")
    else:
        detected = sum(predicted_anomalies)
        metrics["anomalies_detected"] = detected
        log.info(f"Detected {detected} anomalous windows (no ground truth for this split)")

    with open(config.METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    log.info(f"Metrics saved → {config.METRICS_FILE}")

    # Full dataset evaluation plot
    full_features = ["value", "rate_of_change", "rolling_std", "rolling_mean"]
    available = [c for c in full_features if c in full_df.columns]
    full_values = full_df[available].values
    full_seqs = create_sequences(full_values, config.SEQ_LENGTH)
    full_dataset = torch.utils.data.TensorDataset(full_seqs)
    full_loader = torch.utils.data.DataLoader(full_dataset, batch_size=config.BATCH_SIZE * 4, num_workers=0)

    all_losses = compute_losses(trained_model, full_loader, device)

    plot_losses = [None] * config.SEQ_LENGTH + all_losses
    full_df["loss"] = plot_losses
    full_df["detected"] = full_df["loss"] > threshold

    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax1.plot(full_df.index, full_df["value"], label="Sensor Value", color="blue", alpha=0.7)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Sensor Value", color="blue")

    detected_df = full_df[full_df["detected"]]
    ax1.scatter(detected_df.index, detected_df["value"], color="red", label="Anomaly Detected", s=50, zorder=3)

    if "is_anomaly" in full_df.columns:
        gt_df = full_df[full_df["is_anomaly"] & ~full_df["detected"]]
        ax1.scatter(gt_df.index, gt_df["value"], color="orange", label="Missed (FN)", s=30, zorder=2, marker="x")

    ax2 = ax1.twinx()
    ax2.plot(full_df.index, full_df["loss"], label="Reconstruction Loss", color="green", alpha=0.6)
    ax2.axhline(y=threshold, color="r", linestyle="--", label=f"Threshold ({threshold:.4f})")
    ax2.set_ylabel("Loss", color="green")
    ax2.set_ylim(bottom=0)

    title = "Anomaly Detection Results"
    if "f1_score" in metrics:
        title += f" | P={metrics['precision']:.2f} R={metrics['recall']:.2f} F1={metrics['f1_score']:.2f}"
    fig.suptitle(title, fontsize=16)
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.grid(True)

    plot_file = config.PROJECT_ROOT / "anomaly_detection_result.png"
    plt.savefig(plot_file, dpi=150, bbox_inches="tight")
    log.info(f"Plot saved → {plot_file}")


if __name__ == "__main__":
    train_lstm()
