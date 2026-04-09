<div align="center">

# ◈ Anomaly Analog Detector

**Real-time industrial anomaly detection powered by a dual-ML pipeline**

A live monitoring dashboard that visualizes sensor data, corrects ADC non-linearities with an MLP, and detects anomalies using an LSTM autoencoder — all streaming in real time.

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Lightning-ee4c2c?logo=pytorch)](https://pytorch.org/)
[![Ably](https://img.shields.io/badge/Ably-Realtime-ff5416?logo=ably)](https://ably.com/)
[![Deploy](https://img.shields.io/badge/Deploy-Vercel-000?logo=vercel)](https://vercel.com/)

</div>

---

## What This Actually Does

In industrial settings, analog sensors feed signals through an ADC (Analog-to-Digital Converter) that introduces non-linearities. Those distortions make it hard to detect real anomalies.

This project solves that with a **two-stage ML pipeline**:

1. **Stage 1 — ADC Corrector (MLP):** Cleans the raw signal by replacing the traditional look-up table with a trained neural network. Faster, more accurate, deployable on edge hardware.

2. **Stage 2 — Anomaly Detector (LSTM Autoencoder):** Trained only on *normal* data, it learns what "healthy" looks like. When reconstruction error spikes above a dynamically calculated threshold, it flags an anomaly.

The corrected signal and detection results stream to this dashboard in real time via [Ably](https://ably.com/).

```
┌─────────────┐     ┌────────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Raw Sensor  │────▸│  ADC Corrector  │────▸│  LSTM Autoencoder  │────▸│  Dashboard   │
│  Signal      │     │  (MLP)          │     │  (Anomaly Det.)    │     │  (Next.js)   │
└─────────────┘     └────────────────┘     └───────────────────┘     └──────────────┘
                        Stage 1                  Stage 2               Real-time UI
```

## Features

- **Dual-ML pipeline** — correction + detection in sequence for production-grade accuracy
- **Real-time signal chart** — rolling waveform visualization with anomaly markers
- **Live anomaly alerts** — instant visual feedback when the system detects failures
- **Pipeline health monitoring** — see the status of each ML stage at a glance
- **Signal statistics** — live min, max, mean, and standard deviation
- **Reconstruction error gauge** — watch how close the signal is to the anomaly threshold
- **Event log** — timestamped history of all detection events
- **Responsive design** — works on desktop and mobile for field monitoring
- **Edge-ready models** — designed for ONNX export and quantization on TI Sitara hardware
- **Secure token auth** — Ably API keys never touch the browser

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, Recharts, Tailwind CSS 4 |
| **Real-time** | Ably (WebSocket messaging) |
| **ML Pipeline** | Python, PyTorch Lightning, Scikit-learn |
| **Models** | MLP (ADC correction), LSTM Autoencoder (anomaly detection) |
| **Deployment** | Vercel (dashboard), Local/Edge (ML agent) |

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/grizzleyyybear/anomaly-analog-detector.git
cd anomaly-analog-detector
npm install
```

### 2. Configure environment

```bash
cp .env.example .env.local
```

Open `.env.local` and add your [Ably API key](https://ably.com/) (free tier available):

```
ABLY_API_KEY=your-ably-api-key-here
```

### 3. Run the dashboard

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The dashboard will show "Waiting for data..." until the ML agent starts streaming.

### 4. Start the ML agent

The ML pipeline runs separately. Clone and set up the companion repo:

```bash
git clone https://github.com/grizzleyyybear/ml_anomaly_detection.git
cd ml_anomaly_detection
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

Once running, the dashboard will light up with live data.

## Project Structure

```
anomaly-analog-detector/
├── src/
│   └── app/
│       ├── api/
│       │   └── ably-token/
│       │       └── route.js            # Secure token endpoint
│       ├── components/
│       │   ├── SignalChart.js           # Real-time waveform chart
│       │   ├── MetricCard.js            # Reusable metric display
│       │   ├── AnomalyLog.js            # Event history log
│       │   └── PipelineStatus.js        # ML pipeline indicators
│       ├── hooks/
│       │   └── useAbly.js               # Ably connection + data management
│       ├── page.js                      # Main dashboard
│       ├── layout.js                    # App layout + metadata
│       └── globals.css                  # Dashboard theme + styles
├── .env.example                         # Environment template
├── next.config.mjs
└── package.json
```

## How the Pipeline Works

### ADC Corrector (Stage 1)

The MLP replaces the traditional polynomial or LUT-based correction with a learned mapping:

- **Input:** Raw 12-bit ADC reading
- **Output:** Corrected analog value
- **Why ML:** Handles complex non-linearities that polynomial fitting misses, especially at range edges

### LSTM Autoencoder (Stage 2)

Trained exclusively on normal operating data using reconstruction-based anomaly detection:

- **Input:** Sliding window of corrected signal values
- **Output:** Reconstructed signal + reconstruction error
- **Anomaly decision:** Error > dynamic threshold (mean + 3σ of training errors)
- **Why LSTM:** Captures temporal dependencies in the signal that feed-forward networks miss

### Dynamic Thresholding

No magic numbers. The threshold is computed from the model's own performance on validation data:

```
threshold = mean(validation_errors) + 3 × std(validation_errors)
```

This adapts to each deployment automatically.

## Deployment

### Dashboard (Vercel)

```bash
npm run build
vercel deploy
```

Set `ABLY_API_KEY` in your Vercel project's environment variables.

### ML Agent (Edge / Local)

The ML agent is designed for deployment on edge hardware:

- Export models to ONNX with `torch.onnx.export()`
- Quantize to INT8 for TI Sitara AM62x / AM64x
- Run inference with ONNX Runtime or TI's Edge AI SDK

## Companion Repository

The ML pipeline (training, inference, agent) lives here:

**→ [ml_anomaly_detection](https://github.com/grizzleyyybear/ml_anomaly_detection)**

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feat/your-feature`)
5. Open a Pull Request

## License

MIT

---

<div align="center">
  <sub>Built for industrial signal monitoring. Designed for the edge.</sub>
</div>
