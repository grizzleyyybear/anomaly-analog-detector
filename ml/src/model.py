import torch
import torch.nn as nn
import pytorch_lightning as pl


class LSTMAutoencoder(pl.LightningModule):

    def __init__(self, input_size=1, hidden_size=64, seq_len=100, learning_rate=1e-3, num_layers=1):
        super().__init__()
        self.save_hyperparameters()
        self.learning_rate = learning_rate

        self.encoder = nn.LSTM(
            input_size=self.hparams.input_size,
            hidden_size=self.hparams.hidden_size,
            num_layers=self.hparams.num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0,
        )

        self.decoder = nn.LSTM(
            input_size=self.hparams.hidden_size,
            hidden_size=self.hparams.hidden_size,
            num_layers=self.hparams.num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0,
        )

        self.output_layer = nn.Linear(self.hparams.hidden_size, self.hparams.input_size)
        self.criterion = nn.MSELoss()

    def forward(self, x):
        _, (hidden, cell) = self.encoder(x)
        context = hidden[-1].unsqueeze(1).repeat(1, self.hparams.seq_len, 1)
        decoded, _ = self.decoder(context)
        return self.output_layer(decoded)

    def training_step(self, batch, batch_idx):
        x, y = batch
        output = self(x)
        loss = self.criterion(output, y)
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)
