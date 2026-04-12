import logging
import torch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from model import LSTMAutoencoder
from corrector_model import load_corrector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def export_lstm():
    if not config.LSTM_CHECKPOINT.exists():
        log.error(f"LSTM checkpoint not found: {config.LSTM_CHECKPOINT}")
        log.error("Run train_and_evaluate.py first")
        return False

    model = LSTMAutoencoder.load_from_checkpoint(str(config.LSTM_CHECKPOINT))
    model.eval()
    model.to("cpu")

    n_features = model.hparams.input_size
    seq_len = model.hparams.seq_len
    dummy = torch.randn(1, seq_len, n_features)

    config.ONNX_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.ONNX_DIR / "lstm_autoencoder.onnx"

    torch.onnx.export(
        model,
        dummy,
        str(out_path),
        input_names=["signal_window"],
        output_names=["reconstruction"],
        dynamic_axes={
            "signal_window": {0: "batch_size"},
            "reconstruction": {0: "batch_size"},
        },
        opset_version=17,
    )
    log.info(f"LSTM exported → {out_path} (input: [{seq_len}, {n_features}])")
    return True


def export_corrector():
    if not config.CORRECTOR_CHECKPOINT.exists():
        log.error(f"Corrector checkpoint not found: {config.CORRECTOR_CHECKPOINT}")
        log.error("Run corrector_model.py first")
        return False

    model, x_max, y_max = load_corrector()
    model.to("cpu")

    dummy = torch.randn(1, 1)

    config.ONNX_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.ONNX_DIR / "adc_corrector.onnx"

    torch.onnx.export(
        model,
        dummy,
        str(out_path),
        input_names=["raw_adc_normalized"],
        output_names=["corrected_adc_normalized"],
        dynamic_axes={
            "raw_adc_normalized": {0: "batch_size"},
            "corrected_adc_normalized": {0: "batch_size"},
        },
        opset_version=17,
    )

    import json
    meta_path = config.ONNX_DIR / "corrector_meta.json"
    with open(meta_path, "w") as f:
        json.dump({"x_max": x_max, "y_max": y_max}, f, indent=2)

    log.info(f"Corrector exported → {out_path} (x_max={x_max:.2f}, y_max={y_max:.2f})")
    return True


def verify_onnx():
    try:
        import onnxruntime as ort
    except ImportError:
        log.warning("onnxruntime not installed — skipping verification (pip install onnxruntime)")
        return

    lstm_path = config.ONNX_DIR / "lstm_autoencoder.onnx"
    corrector_path = config.ONNX_DIR / "adc_corrector.onnx"

    if lstm_path.exists():
        sess = ort.InferenceSession(str(lstm_path))
        inp = sess.get_inputs()[0]
        out = sess.get_outputs()[0]
        log.info(f"LSTM ONNX verified — input: {inp.shape}, output: {out.shape}")

    if corrector_path.exists():
        sess = ort.InferenceSession(str(corrector_path))
        inp = sess.get_inputs()[0]
        out = sess.get_outputs()[0]
        log.info(f"Corrector ONNX verified — input: {inp.shape}, output: {out.shape}")


if __name__ == "__main__":
    log.info("Exporting models to ONNX")
    export_corrector()
    export_lstm()
    verify_onnx()
    log.info("Done")
