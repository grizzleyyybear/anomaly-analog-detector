import os
from pathlib import Path
from dotenv import load_dotenv

ML_ROOT = Path(__file__).parent
PROJECT_ROOT = ML_ROOT.parent

load_dotenv(ML_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

DATA_DIR = ML_ROOT / "data"
CHECKPOINT_DIR = ML_ROOT / "checkpoints"
THRESHOLD_FILE = CHECKPOINT_DIR / "threshold.json"
METRICS_FILE = CHECKPOINT_DIR / "eval_metrics.json"
CORRECTOR_CHECKPOINT = CHECKPOINT_DIR / "adc_corrector.pt"
LSTM_CHECKPOINT = CHECKPOINT_DIR / "best-model.ckpt"
ONNX_DIR = CHECKPOINT_DIR / "onnx"

ABLY_API_KEY = os.getenv("ABLY_API_KEY")

# Signal generation
SIGNAL_PERIODS = 5000
SIGNAL_FREQ = "s"
NOISE_STD = 0.1
ADC_BITS = 12
ADC_RANGE = 2 ** ADC_BITS
ADC_INL_AMPLITUDE = 8.0
ADC_DNL_STD = 0.3

# Anomaly injection types and regions
ANOMALY_REGIONS = [
    {"start": 900,  "end": 910,  "type": "spike",       "magnitude": 5.0},
    {"start": 1800, "end": 1830, "type": "drift",        "rate": 0.15},
    {"start": 2700, "end": 2720, "type": "oscillation",  "amplitude": 2.0, "freq": 3.0},
    {"start": 3500, "end": 3520, "type": "drop",         "magnitude": -3.0},
    {"start": 4200, "end": 4240, "type": "noise_burst",  "std": 1.5},
]

# Feature engineering
N_FEATURES = 4           # value, rate_of_change, rolling_std, rolling_mean
ROLLING_WINDOW = 10

# Data splits
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Training
SEQ_LENGTH = 100
BATCH_SIZE = 64
LSTM_HIDDEN_SIZE = 64
LSTM_EPOCHS = 30
LSTM_LR = 1e-3
CORRECTOR_EPOCHS = 200
CORRECTOR_LR = 1e-3
THRESHOLD_SIGMA = 3

# Live agent
AGENT_TICK_RATE = 0.1
AGENT_TOTAL_STEPS = 10000
