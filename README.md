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

## What's in here

```
src/app/
├── api/ably-token/route.js     # secure token endpoint (key never hits the browser)
├── components/
│   ├── SignalChart.js           # rolling waveform with anomaly markers
│   ├── MetricCard.js            # reusable stat card
│   ├── AnomalyLog.js            # timestamped event history
│   └── PipelineStatus.js        # connection → stage 1 → stage 2 indicators
├── hooks/useAbly.js             # all real-time data logic
├── page.js                      # main dashboard
├── layout.js
└── globals.css
```

## Deploy

```bash
npm run build && vercel deploy
```

Set `ABLY_API_KEY` in Vercel's environment variables.

## ML agent

The models and inference pipeline live in a separate repo: **[ml_anomaly_detection](https://github.com/grizzleyyybear/ml_anomaly_detection)**

## License

MIT
