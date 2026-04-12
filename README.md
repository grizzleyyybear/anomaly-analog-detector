<div align="center">

# ◈ Anomaly Analog Detector

A live dashboard for watching an ML pipeline catch industrial sensor failures in real time.

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![Ably](https://img.shields.io/badge/Ably-Realtime-ff5416?logo=ably)](https://ably.com/)
[![Deploy](https://img.shields.io/badge/Deploy-Vercel-000?logo=vercel)](https://vercel.com/)

</div>

---

## What this is

A Python agent runs two ML models back-to-back — one corrects ADC distortion, the other catches anomalies — and streams the results here at 10 Hz. This is the monitoring frontend.

```
Sensor → ADC Corrector → LSTM Autoencoder → Ably → This Dashboard
```

You get a rolling signal chart, live anomaly alerts, pipeline health indicators, reconstruction error gauges, and a timestamped event log. Works on desktop and mobile.

## Tech stack

Next.js 15 · React 19 · Recharts · Tailwind CSS 4 · Ably WebSockets · Vercel

## Setup

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

The ML pipeline lives in the `ml/` directory of this repo:

```bash
cd ml
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your Ably key
python src/generate_data.py
python src/corrector_model.py
cd src && python train_and_evaluate.py && cd ..
python live_agent.py
```

Once running, the dashboard will light up with live data.

## What's in here

```
src/app/                             # Next.js dashboard
├── api/ably-token/route.js          # secure token endpoint
├── components/                      # SignalChart, MetricCard, AnomalyLog, PipelineStatus
├── hooks/useAbly.js                 # real-time data logic
├── page.js                          # main dashboard
└── globals.css

ml/                                  # Python ML pipeline
├── config.py                        # all hyperparameters
├── live_agent.py                    # real-time inference → Ably
├── requirements.txt
├── src/
│   ├── generate_data.py             # synthetic data + 5 anomaly types
│   ├── corrector_model.py           # ADC Corrector MLP
│   ├── model.py                     # LSTM Autoencoder
│   ├── data_preprocessing.py        # train/val/test split + feature engineering
│   ├── train_and_evaluate.py        # training + P/R/F1 evaluation
│   └── export_onnx.py              # ONNX export for edge deployment
├── checkpoints/                     # trained weights + metrics (gitignored)
└── data/                            # generated CSVs (gitignored)
```

## Deploy

```bash
npm run build && vercel deploy
```

Set `ABLY_API_KEY` in Vercel's environment variables.

## Running the ML pipeline

```bash
cd ml
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # add your Ably key

python src/generate_data.py            # generate training data
python src/corrector_model.py          # train Stage 1
cd src && python train_and_evaluate.py # train Stage 2 + evaluate
python export_onnx.py                  # export to ONNX
cd .. && python live_agent.py          # start streaming to dashboard
```

## License

MIT
