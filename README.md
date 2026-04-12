<div align="center">

# ◈ Anomaly Analog Detector

**Real-time anomaly detection on industrial sensor signals using a dual-ML pipeline.**

[![CI](https://github.com/grizzleyyybear/anomaly-analog-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/grizzleyyybear/anomaly-analog-detector/actions)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178c6?logo=typescript)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Lightning-ee4c2c?logo=pytorch)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

> **Demo**: Run `npm run dev` + `python ml/live_agent.py` and open [localhost:3000](http://localhost:3000) to see the dashboard live. The ML agent generates synthetic sensor data with injected anomalies, so you can see the full pipeline working out of the box — no real hardware needed.

---

## What it does

A Python agent reads sensor data, runs it through two ML models back-to-back, and streams the results over WebSockets. A Next.js dashboard picks them up and shows everything live — signal waveforms, anomaly alerts, pipeline health, reconstruction error gauges.

```
Sensor Signal → ADC Corrector (MLP) → LSTM Autoencoder → Ably WebSocket → Dashboard
```

**Stage 1** corrects analog-to-digital converter nonlinearity (INL/DNL errors).
**Stage 2** detects anomalies via reconstruction error — if the LSTM can't reconstruct a signal window, something's wrong.

## Key features

| Feature | Details |
|---------|---------|
| **Dual-ML Pipeline** | ADC Corrector MLP + LSTM Autoencoder running in series |
| **5 Anomaly Types** | Spike, drop, drift, oscillation, noise burst detection |
| **4 Engineered Features** | Value, rate of change, rolling std, rolling mean |
| **Real-time Streaming** | 10 Hz inference with Ably WebSocket delivery |
| **Dynamic Thresholding** | Mean + 3σ from validation set (no hardcoded cutoffs) |
| **ONNX Export** | Both models exportable for edge deployment |
| **Train/Val/Test Split** | 70/15/15 with P/R/F1 evaluation on held-out test set |
| **Feature Normalization** | StandardScaler persisted and shared between training and inference |
| **TypeScript (strict)** | Fully typed React components, hooks, and API routes |
| **Accessible UI** | ARIA roles, labels, live regions — screen reader friendly |
| **Security Headers** | CSP, HSTS, X-Frame-Options, Permissions-Policy |
| **Docker Ready** | Multi-stage Dockerfile + docker-compose for both services |
| **CI/CD** | GitHub Actions: lint, build, test on every push |
| **Pre-commit Hooks** | Husky + lint-staged — linting runs before every commit |
| **Code Coverage** | Vitest V8 coverage with `npm run test:coverage` |
| **Model Versioning** | `model_metadata.json` tracking data hash, hyperparams, metrics |
| **Health Monitoring** | `/api/health` endpoint with uptime, version, status |
| **Error Boundaries** | React ErrorBoundary for graceful crash recovery |

## Architecture

```
anomaly-analog-detector/
├── src/app/                          # Next.js 15 dashboard (TypeScript)
│   ├── api/
│   │   ├── ably-token/route.ts       # secure WebSocket token endpoint
│   │   └── health/route.ts           # health check endpoint
│   ├── components/
│   │   ├── SignalChart.tsx            # rolling waveform with anomaly markers
│   │   ├── MetricCard.tsx             # live metric display cards
│   │   ├── AnomalyLog.tsx            # timestamped event history
│   │   ├── PipelineStatus.tsx         # stage health indicators
│   │   └── ErrorBoundary.tsx          # crash recovery wrapper
│   ├── hooks/useAbly.ts              # WebSocket connection + state management
│   ├── __tests__/                    # Vitest test suite
│   ├── page.tsx                      # dashboard composition
│   └── globals.css                   # dark industrial theme
│
├── ml/                               # Python ML pipeline
│   ├── config.py                     # centralized hyperparameters + paths
│   ├── live_agent.py                 # real-time inference → Ably streaming
│   ├── preflight.py                  # environment validation script
│   ├── src/
│   │   ├── generate_data.py          # synthetic sensor data + 5 anomaly types
│   │   ├── corrector_model.py        # ADC Corrector MLP (1→64→64→32→1)
│   │   ├── model.py                  # LSTM Autoencoder (PyTorch Lightning)
│   │   ├── data_preprocessing.py     # scaling, splitting, sequence creation
│   │   ├── train_and_evaluate.py     # training + threshold + P/R/F1 metrics
│   │   ├── export_onnx.py           # ONNX export with verification
│   │   └── version_model.py         # model metadata + dataset hashing
│   └── tests/
│       └── test_pipeline.py          # pytest suite for ML components
│
├── .github/workflows/ci.yml         # GitHub Actions CI pipeline
├── .husky/pre-commit                 # pre-commit lint hook
├── Dockerfile                        # dashboard container (multi-stage)
├── ml/Dockerfile                     # ML agent container
├── docker-compose.yml                # full-stack orchestration
├── tsconfig.json                     # TypeScript strict mode config
└── CONTRIBUTING.md                   # contribution guidelines
```

## Getting started

### Prerequisites

- Node.js 20+
- Python 3.10+
- [Ably account](https://ably.com/) (free tier works)

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

Add your Ably API key to `.env.local`:

```
ABLY_API_KEY=your-key-here
```

### 3. Run the dashboard

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). It'll show "Waiting for data..." until the ML agent starts.

### 4. Train and run the ML pipeline

```bash
cd ml
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # add the same Ably key

# Validate environment
python preflight.py

# Train pipeline
python src/generate_data.py            # generate synthetic sensor data
python src/corrector_model.py          # train Stage 1 (ADC Corrector)
cd src && python train_and_evaluate.py && cd ..   # train Stage 2 + evaluate

# Start streaming
python live_agent.py
```

### 5. Or use Docker

```bash
echo "ABLY_API_KEY=your-key-here" > .env
docker compose up --build
```

## Running tests

```bash
# Dashboard tests
npm test

# Dashboard tests with coverage
npm run test:coverage

# ML tests
cd ml && python -m pytest tests/ -v
```

## ML pipeline details

### Model architectures

**ADC Corrector** — 4-layer MLP that learns the inverse of ADC nonlinearity:
```
Input(1) → Linear(64) → ReLU → Linear(64) → ReLU → Linear(32) → ReLU → Linear(1)
```

**LSTM Autoencoder** — encodes a signal window into a latent vector, then tries to reconstruct it:
```
Encoder: LSTM(4, 64) → context vector
Decoder: LSTM(64, 64) → Linear(64, 4) → reconstructed window
Loss: MSE between input and reconstruction
```

### Anomaly detection logic

The autoencoder is trained only on normal data. At inference time, high reconstruction error means the model hasn't seen that pattern before → anomaly.

Threshold is computed dynamically: `mean + 3σ` of validation set reconstruction errors. No manual tuning needed.

### Evaluation metrics

The test set includes both normal and anomalous windows. After training, the pipeline reports:

- **Precision** — how many flagged anomalies are real
- **Recall** — how many real anomalies got caught
- **F1 Score** — harmonic mean of precision and recall
- **Confusion Matrix** — TP, FP, TN, FN breakdown

## Deploy

### Vercel (dashboard only)

```bash
npm run build && vercel deploy
```

Set `ABLY_API_KEY` in Vercel environment variables.

### Docker (full stack)

```bash
docker compose up -d
```

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript (strict), Recharts, Tailwind CSS 4 |
| Backend API | Next.js Route Handlers (security headers, health checks) |
| ML Framework | PyTorch, PyTorch Lightning |
| Data Processing | scikit-learn, pandas, NumPy |
| Real-time | Ably WebSockets |
| Export | ONNX Runtime |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | Vitest + Testing Library + V8 coverage, pytest |
| Code Quality | ESLint, Husky, lint-staged |

## License

[MIT](LICENSE)
