import asyncio
import json
import signal
import sys
import logging
from collections import deque
from datetime import datetime, timezone

import numpy as np
import torch
from ably import AblyRealtime

import config
from src.model import LSTMAutoencoder
from src.corrector_model import load_corrector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("agent")

shutdown_event = asyncio.Event()


def load_threshold():
    if not config.THRESHOLD_FILE.exists():
        log.warning("threshold.json not found — using fallback threshold")
        return config.FALLBACK_THRESHOLD, {}
    try:
        with open(config.THRESHOLD_FILE) as f:
            data = json.load(f)
        if "threshold" not in data:
            raise ValueError("Missing 'threshold' key")
        log.info(f"Threshold loaded: {data['threshold']:.6f} (mean={data['mean_loss']:.6f}, {data['sigma']}σ)")
        return data["threshold"], data
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        log.warning(f"Failed to parse threshold.json: {e} — using fallback")
        return config.FALLBACK_THRESHOLD, {}


def load_models():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log.info(f"Device: {device}")

    corrector, x_max, y_max = None, 1.0, 1.0
    if config.CORRECTOR_CHECKPOINT.exists():
        corrector, x_max, y_max = load_corrector()
        corrector.to(device)
        log.info("Stage 1 — ADC Corrector loaded ✓")
    else:
        log.warning("Stage 1 — ADC Corrector not found, passing raw values through")

    if not config.LSTM_CHECKPOINT.exists():
        log.error(f"LSTM checkpoint not found at {config.LSTM_CHECKPOINT}")
        sys.exit(1)

    lstm_model = LSTMAutoencoder.load_from_checkpoint(str(config.LSTM_CHECKPOINT))
    lstm_model.to(device)
    lstm_model.eval()
    n_features = lstm_model.hparams.input_size
    log.info(f"Stage 2 — LSTM Autoencoder loaded ✓ (features={n_features})")

    threshold, threshold_meta = load_threshold()

    scaler = None
    if config.SCALER_FILE.exists():
        import joblib
        scaler = joblib.load(str(config.SCALER_FILE))
        log.info("Feature scaler loaded ✓")
    else:
        log.warning("scaler.joblib not found — features will not be normalized")

    return corrector, x_max, y_max, lstm_model, threshold, n_features, device, scaler


class FeatureBuffer:
    """Maintains a sliding window and computes derived features in real time."""

    def __init__(self, seq_length, rolling_window=10):
        self.seq_length = seq_length
        self.rolling_window = rolling_window
        self.raw_history = deque(maxlen=seq_length + rolling_window)
        self.prev_value = None

    def push(self, value):
        self.raw_history.append(value)
        rate = (value - self.prev_value) if self.prev_value is not None else 0.0
        self.prev_value = value

        window = list(self.raw_history)[-self.rolling_window:]
        rolling_std = float(np.std(window)) if len(window) >= 2 else 0.0
        rolling_mean = float(np.mean(window))

        return [value, rate, rolling_std, rolling_mean]

    def scale(self, window, scaler):
        """Apply the training scaler to a window of features."""
        window_array = np.array(window)
        return scaler.transform(window_array)

    @property
    def ready(self):
        return len(self.raw_history) >= self.seq_length


async def run_pipeline():
    if not config.ABLY_API_KEY:
        log.error("ABLY_API_KEY not set. Create a .env file (see .env.example)")
        sys.exit(1)

    corrector, x_max, y_max, lstm_model, threshold, n_features, device, scaler = load_models()

    ably = AblyRealtime(config.ABLY_API_KEY)
    await ably.connection.once_async("connected")
    log.info("Connected to Ably ✓")

    signal_channel = ably.channels.get("signal-channel")
    anomaly_channel = ably.channels.get("anomaly-channel")

    feature_buf = FeatureBuffer(config.SEQ_LENGTH, config.ROLLING_WINDOW)
    feature_history = deque(maxlen=config.SEQ_LENGTH)
    anomaly_count = 0

    log.info(f"Starting inference ({config.AGENT_TOTAL_STEPS} steps @ {1/config.AGENT_TICK_RATE:.0f} Hz, {n_features} features)")

    for step in range(config.AGENT_TOTAL_STEPS):
        if shutdown_event.is_set():
            log.info("Shutdown requested")
            break

        now = datetime.now(timezone.utc).isoformat()

        raw_value = np.sin(step * 0.1) + np.random.normal(0, 0.05)
        is_anomaly_injection = step % 200 > 180
        if is_anomaly_injection:
            raw_value += 5.0

        # Stage 1: ADC Correction
        if corrector is not None:
            with torch.no_grad():
                inp = torch.tensor([[raw_value / x_max]], dtype=torch.float32).to(device)
                corrected_value = corrector(inp).item() * y_max
            stage1_status = "active"
        else:
            corrected_value = raw_value
            stage1_status = "idle"

        # Compute features
        features = feature_buf.push(corrected_value)
        feature_history.append(features)

        # Stage 2: Anomaly Detection
        status = "Normal"
        reconstruction_error = None
        stage2_status = "idle"

        if feature_buf.ready and len(feature_history) >= config.SEQ_LENGTH:
            stage2_status = "active"
            window = list(feature_history)[-config.SEQ_LENGTH:]

            # Scale features if scaler is available, then trim to model input size
            if scaler is not None:
                window_array = np.array(window)
                window_scaled = scaler.transform(window_array)
                tensor_data = window_scaled[:, :n_features].tolist()
            else:
                tensor_data = [f[:n_features] for f in window]

            input_tensor = torch.tensor([tensor_data], dtype=torch.float32).to(device)

            with torch.no_grad():
                reconstruction = lstm_model(input_tensor)
                reconstruction_error = torch.mean((input_tensor - reconstruction) ** 2).item()

            if reconstruction_error > threshold:
                status = "Anomaly Detected"
                anomaly_count += 1

        # Publish
        await signal_channel.publish("update", {
            "value": round(corrected_value, 6),
            "rawValue": round(raw_value, 6),
            "correctedValue": round(corrected_value, 6),
            "timestamp": now,
            "stage1Status": stage1_status,
        })

        await anomaly_channel.publish("update", {
            "status": status,
            "timestamp": now,
            "reconstructionError": round(reconstruction_error, 8) if reconstruction_error is not None else None,
            "threshold": round(threshold, 8),
            "stage2Status": stage2_status,
        })

        if step % 50 == 0:
            err_str = f"{reconstruction_error:.6f}" if reconstruction_error is not None else "buffering"
            log.info(f"step={step:>5} | signal={corrected_value:+.4f} | error={err_str} | {status} | anomalies={anomaly_count}")

        await asyncio.sleep(config.AGENT_TICK_RATE)

    await ably.close()
    log.info(f"Done. Total anomalies: {anomaly_count}")


def handle_shutdown(loop):
    shutdown_event.set()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_shutdown, loop)
        except NotImplementedError:
            signal.signal(sig, lambda s, f: shutdown_event.set())
    loop.run_until_complete(run_pipeline())
