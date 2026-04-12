"""Tests for the ML pipeline components."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import config


class TestConfig:
    def test_paths_exist_as_path_objects(self):
        assert isinstance(config.ML_ROOT, Path)
        assert isinstance(config.DATA_DIR, Path)
        assert isinstance(config.CHECKPOINT_DIR, Path)

    def test_hyperparameters_are_sensible(self):
        assert config.SEQ_LENGTH > 0
        assert config.BATCH_SIZE > 0
        assert config.N_FEATURES == 4
        assert 0 < config.TRAIN_RATIO < 1
        assert config.TRAIN_RATIO + config.VAL_RATIO + config.TEST_RATIO == pytest.approx(1.0)

    def test_fallback_threshold_defined(self):
        assert hasattr(config, 'FALLBACK_THRESHOLD')
        assert config.FALLBACK_THRESHOLD > 0

    def test_scaler_file_path_defined(self):
        assert hasattr(config, 'SCALER_FILE')
        assert str(config.SCALER_FILE).endswith('.joblib')


class TestGenerateData:
    def test_inject_anomalies_marks_correct_regions(self):
        from generate_data import inject_anomalies
        n = 5000
        values = np.zeros(n)
        modified, mask = inject_anomalies(values, n)
        assert mask.sum() > 0
        assert mask.sum() < n
        assert not np.array_equal(values, modified)

    def test_add_engineered_features(self):
        from generate_data import add_engineered_features
        df = pd.DataFrame({"value": np.random.randn(100)})
        result = add_engineered_features(df.copy())
        assert "rate_of_change" in result.columns
        assert "rolling_std" in result.columns
        assert "rolling_mean" in result.columns
        assert len(result) == 100

    def test_simulate_adc_nonlinearity(self):
        from generate_data import simulate_adc_nonlinearity
        ideal = np.linspace(0, config.ADC_RANGE - 1, 100)
        distorted = simulate_adc_nonlinearity(ideal)
        assert len(distorted) == len(ideal)
        assert distorted.min() >= 0
        assert distorted.max() < config.ADC_RANGE


class TestDataPreprocessing:
    def test_create_sequences_shape(self):
        from data_preprocessing import create_sequences
        data = np.random.randn(200, 4)
        seqs = create_sequences(data, seq_length=50)
        assert seqs.shape == (150, 50, 4)
        assert seqs.dtype == torch.float32

    def test_create_sequences_single_feature(self):
        from data_preprocessing import create_sequences
        data = np.random.randn(100, 1)
        seqs = create_sequences(data, seq_length=20)
        assert seqs.shape == (80, 20, 1)

    def test_split_ratios(self):
        from data_preprocessing import split_data
        df = pd.DataFrame({"x": range(1000)})
        train, val, test = split_data(df)
        assert len(train) == 700
        assert len(val) == 150
        assert len(test) == 150


class TestModel:
    def test_lstm_autoencoder_forward_pass(self):
        from model import LSTMAutoencoder
        model = LSTMAutoencoder(input_size=4, hidden_size=32, seq_len=50)
        x = torch.randn(2, 50, 4)
        output = model(x)
        assert output.shape == x.shape

    def test_lstm_autoencoder_single_feature(self):
        from model import LSTMAutoencoder
        model = LSTMAutoencoder(input_size=1, hidden_size=16, seq_len=20)
        x = torch.randn(1, 20, 1)
        output = model(x)
        assert output.shape == (1, 20, 1)

    def test_reconstruction_loss_is_low_for_simple_signal(self):
        from model import LSTMAutoencoder
        model = LSTMAutoencoder(input_size=1, hidden_size=32, seq_len=50)
        x = torch.zeros(1, 50, 1)
        output = model(x)
        loss = torch.mean((x - output) ** 2).item()
        assert loss < 10.0  # untrained but should not be absurdly large


class TestCorrectorModel:
    def test_corrector_forward(self):
        from corrector_model import ADCCorrector
        model = ADCCorrector()
        x = torch.randn(10, 1)
        out = model(x)
        assert out.shape == (10, 1)

    def test_correct_method(self):
        from corrector_model import ADCCorrector
        model = ADCCorrector()
        result = model.correct(0.5)
        assert isinstance(result, float)
