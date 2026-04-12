"""Generate model_metadata.json after training.

Records training date, dataset hash, hyperparameters, and evaluation
metrics so every checkpoint is traceable back to its training run.
"""

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

log = logging.getLogger(__name__)


def hash_file(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_metadata():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    metadata = {
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "framework": "pytorch-lightning",
        "hyperparameters": {
            "seq_length": config.SEQ_LENGTH,
            "batch_size": config.BATCH_SIZE,
            "lstm_hidden_size": config.LSTM_HIDDEN_SIZE,
            "lstm_epochs": config.LSTM_EPOCHS,
            "lstm_lr": config.LSTM_LR,
            "corrector_epochs": config.CORRECTOR_EPOCHS,
            "corrector_lr": config.CORRECTOR_LR,
            "n_features": config.N_FEATURES,
            "threshold_sigma": config.THRESHOLD_SIGMA,
            "train_ratio": config.TRAIN_RATIO,
            "val_ratio": config.VAL_RATIO,
            "test_ratio": config.TEST_RATIO,
        },
        "data": {},
        "checkpoints": {},
        "evaluation": {},
    }

    data_file = config.DATA_DIR / "sensor_data.csv"
    if data_file.exists():
        metadata["data"] = {
            "file": data_file.name,
            "sha256": hash_file(data_file),
            "size_bytes": data_file.stat().st_size,
        }

    for name, path in [
        ("lstm", config.LSTM_CHECKPOINT),
        ("corrector", config.CORRECTOR_CHECKPOINT),
        ("scaler", config.SCALER_FILE),
    ]:
        if path.exists():
            metadata["checkpoints"][name] = {
                "file": path.name,
                "sha256": hash_file(path),
                "size_bytes": path.stat().st_size,
            }

    if config.METRICS_FILE.exists():
        with open(config.METRICS_FILE) as f:
            metadata["evaluation"] = json.load(f)

    if config.THRESHOLD_FILE.exists():
        with open(config.THRESHOLD_FILE) as f:
            threshold_data = json.load(f)
            metadata["threshold"] = threshold_data

    out_path = config.CHECKPOINT_DIR / "model_metadata.json"
    config.CHECKPOINT_DIR.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(metadata, f, indent=2)

    log.info(f"Model metadata saved → {out_path}")
    log.info(f"  Version: {metadata['version']}")
    log.info(f"  Data hash: {metadata['data'].get('sha256', 'n/a')[:12]}...")
    log.info(f"  Checkpoints: {list(metadata['checkpoints'].keys())}")
    return metadata


if __name__ == "__main__":
    generate_metadata()
