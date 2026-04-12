"""Pre-flight checks for the ML pipeline.

Run before live_agent.py to verify that all dependencies,
checkpoints, and environment variables are properly configured.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("preflight")

REQUIRED_PACKAGES = [
    ("torch", "torch"),
    ("pytorch_lightning", "pytorch-lightning"),
    ("sklearn", "scikit-learn"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("ably", "ably"),
    ("dotenv", "python-dotenv"),
    ("joblib", "joblib"),
]

OPTIONAL_PACKAGES = [
    ("onnx", "onnx"),
    ("onnxruntime", "onnxruntime"),
]


def check_packages():
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
            log.error(f"✗ {pip_name} not installed")

    for import_name, pip_name in OPTIONAL_PACKAGES:
        try:
            __import__(import_name)
            log.info(f"✓ {pip_name}")
        except ImportError:
            log.warning(f"⚠ {pip_name} not installed (optional — needed for ONNX export)")

    if missing:
        log.error(f"Missing required packages: {', '.join(missing)}")
        log.error(f"Run: pip install {' '.join(missing)}")
        return False

    for import_name, pip_name in REQUIRED_PACKAGES:
        log.info(f"✓ {pip_name}")
    return True


def check_config():
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import config

    ok = True

    if not config.ABLY_API_KEY:
        log.error("✗ ABLY_API_KEY not set — create ml/.env or project root .env.local")
        ok = False
    else:
        masked = config.ABLY_API_KEY[:8] + "..." + config.ABLY_API_KEY[-4:]
        log.info(f"✓ ABLY_API_KEY configured ({masked})")

    config.DATA_DIR.mkdir(exist_ok=True)
    config.CHECKPOINT_DIR.mkdir(exist_ok=True)
    log.info(f"✓ Data directory: {config.DATA_DIR}")
    log.info(f"✓ Checkpoint directory: {config.CHECKPOINT_DIR}")

    data_file = config.DATA_DIR / "sensor_data.csv"
    if not data_file.exists():
        log.warning("⚠ sensor_data.csv not found — run: python src/generate_data.py")

    if not config.CORRECTOR_CHECKPOINT.exists():
        log.warning("⚠ ADC Corrector checkpoint not found — run: python src/corrector_model.py")

    if not config.LSTM_CHECKPOINT.exists():
        log.error("✗ LSTM checkpoint not found — run: cd src && python train_and_evaluate.py")
        ok = False
    else:
        log.info(f"✓ LSTM checkpoint: {config.LSTM_CHECKPOINT.name}")

    if not config.THRESHOLD_FILE.exists():
        log.warning("⚠ threshold.json not found — will use fallback threshold")
    else:
        log.info(f"✓ Threshold file: {config.THRESHOLD_FILE.name}")

    if not config.SCALER_FILE.exists():
        log.warning("⚠ scaler.joblib not found — features will not be normalized (reduced accuracy)")
    else:
        log.info(f"✓ Feature scaler: {config.SCALER_FILE.name}")

    return ok


def main():
    log.info("=" * 50)
    log.info("ML Pipeline Pre-flight Check")
    log.info("=" * 50)

    pkg_ok = check_packages()
    if not pkg_ok:
        log.error("Fix missing packages before continuing")
        sys.exit(1)

    log.info("")
    cfg_ok = check_config()

    log.info("")
    if cfg_ok:
        log.info("All checks passed — ready to run live_agent.py")
    else:
        log.error("Some checks failed — fix the issues above before running the agent")
        sys.exit(1)


if __name__ == "__main__":
    main()
