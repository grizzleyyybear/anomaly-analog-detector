import logging
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
import config

log = logging.getLogger(__name__)


def simulate_adc_nonlinearity(ideal_codes):
    n = len(ideal_codes)
    inl = config.ADC_INL_AMPLITUDE * np.sin(np.pi * ideal_codes / config.ADC_RANGE)
    dnl = np.random.normal(0, config.ADC_DNL_STD, n)
    distorted = ideal_codes + inl + dnl
    return np.clip(distorted, 0, config.ADC_RANGE - 1)


def inject_anomalies(values, n):
    anomaly_mask = np.zeros(n, dtype=bool)
    anomalies = np.zeros(n)

    for region in config.ANOMALY_REGIONS:
        s, e = region["start"], region["end"]
        if s >= n or e > n:
            continue
        anomaly_mask[s:e] = True
        t = region["type"]

        if t == "spike" or t == "drop":
            anomalies[s:e] = region["magnitude"]
        elif t == "drift":
            length = e - s
            anomalies[s:e] = np.cumsum(np.full(length, region["rate"]))
        elif t == "oscillation":
            length = e - s
            anomalies[s:e] = region["amplitude"] * np.sin(
                np.linspace(0, region["freq"] * 2 * np.pi, length)
            )
        elif t == "noise_burst":
            length = e - s
            anomalies[s:e] = np.random.normal(0, region["std"], length)

    return values + anomalies, anomaly_mask


def add_engineered_features(df, value_col="value"):
    w = config.ROLLING_WINDOW
    df["rate_of_change"] = df[value_col].diff().fillna(0)
    df["rolling_std"] = df[value_col].rolling(w, min_periods=1).std().fillna(0)
    df["rolling_mean"] = df[value_col].rolling(w, min_periods=1).mean().fillna(0)
    return df


def generate_sensor_data():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    np.random.seed(42)
    n = config.SIGNAL_PERIODS

    timestamps = pd.date_range(start="2025-01-01", periods=n, freq=config.SIGNAL_FREQ)

    analog_signal = np.sin(np.linspace(0, 100, n))
    noise = np.random.normal(0, config.NOISE_STD, n)
    clean_analog = analog_signal + noise

    analog_min, analog_max = clean_analog.min(), clean_analog.max()
    ideal_codes = ((clean_analog - analog_min) / (analog_max - analog_min)) * (config.ADC_RANGE - 1)
    raw_adc_codes = simulate_adc_nonlinearity(ideal_codes)
    raw_values = (raw_adc_codes / (config.ADC_RANGE - 1)) * (analog_max - analog_min) + analog_min

    final_values, anomaly_mask = inject_anomalies(raw_values, n)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "value": final_values,
        "ideal_value": clean_analog,
        "raw_adc_code": raw_adc_codes,
        "ideal_adc_code": ideal_codes,
        "is_anomaly": anomaly_mask,
    })

    df = add_engineered_features(df)

    config.DATA_DIR.mkdir(exist_ok=True)
    out_path = config.DATA_DIR / "sensor_data.csv"
    df.to_csv(out_path, index=False)

    anomaly_types = [r["type"] for r in config.ANOMALY_REGIONS]
    log.info(f"Generated {n} samples with {len(config.ANOMALY_REGIONS)} anomaly regions: {anomaly_types}")
    log.info(f"Anomalous points: {anomaly_mask.sum()} / {n} ({100*anomaly_mask.mean():.1f}%)")
    log.info(f"Saved → {out_path}")
    return df


if __name__ == "__main__":
    generate_sensor_data()
