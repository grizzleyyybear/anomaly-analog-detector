import logging
import torch
import torch.nn as nn
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
import config

log = logging.getLogger(__name__)


class ADCCorrector(nn.Module):

    def __init__(self, input_size=1, output_size=1):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, output_size),
        )

    def forward(self, x):
        return self.network(x)

    def correct(self, raw_value):
        self.eval()
        with torch.no_grad():
            inp = torch.tensor([[raw_value]], dtype=torch.float32)
            return self.forward(inp).item()


def train_corrector():
    import pandas as pd
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    data_path = config.DATA_DIR / "sensor_data.csv"
    if not data_path.exists():
        from generate_data import generate_sensor_data
        generate_sensor_data()

    df = pd.read_csv(data_path)
    normal = df[~df["is_anomaly"]]
    x_train = torch.tensor(normal["raw_adc_code"].values, dtype=torch.float32).unsqueeze(1)
    y_train = torch.tensor(normal["ideal_adc_code"].values, dtype=torch.float32).unsqueeze(1)

    x_max = x_train.max().item()
    y_max = y_train.max().item()
    x_norm = x_train / x_max
    y_norm = y_train / y_max

    model = ADCCorrector()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.CORRECTOR_LR)
    criterion = nn.MSELoss()

    dataset = torch.utils.data.TensorDataset(x_norm, y_norm)
    loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True)

    log.info(f"Training ADC Corrector — {config.CORRECTOR_EPOCHS} epochs")
    model.train()
    for epoch in range(config.CORRECTOR_EPOCHS):
        total_loss = 0
        for xb, yb in loader:
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 50 == 0 or epoch == 0:
            log.info(f"  Epoch {epoch+1:>3}/{config.CORRECTOR_EPOCHS} — loss: {total_loss / len(loader):.8f}")

    config.CHECKPOINT_DIR.mkdir(exist_ok=True)
    torch.save({"model_state_dict": model.state_dict(), "x_max": x_max, "y_max": y_max}, config.CORRECTOR_CHECKPOINT)
    log.info(f"Saved → {config.CORRECTOR_CHECKPOINT}")

    model.eval()
    with torch.no_grad():
        pred = model(x_norm) * y_max
        mae = torch.mean(torch.abs(pred - y_train)).item()
        log.info(f"MAE: {mae:.4f} codes (of {config.ADC_RANGE})")

    return model


def load_corrector():
    checkpoint = torch.load(config.CORRECTOR_CHECKPOINT, map_location="cpu", weights_only=True)
    model = ADCCorrector()
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, checkpoint["x_max"], checkpoint["y_max"]


if __name__ == "__main__":
    train_corrector()
