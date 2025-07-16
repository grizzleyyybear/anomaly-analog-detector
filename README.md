<img width="1912" height="1021" alt="image" src="https://github.com/user-attachments/assets/a884122d-1198-48d6-8b61-502d846fb59c" />
<img width="1918" height="1029" alt="image" src="https://github.com/user-attachments/assets/57f7070d-a81e-4fca-a039-e7f018d4ec19" />
# Real-Time Industrial Anomaly Detection with a Dual-ML Pipeline

This project demonstrates a complete, end-to-end system for real-time anomaly detection in industrial sensor data. It features a dual-ML pipeline for signal correction and anomaly detection, with results broadcast to a live web dashboard. The system is designed with edge deployment in mind, making it suitable for hardware like TI Sitara processors.

**Live Demo:** [Link to your deployed Vercel Dashboard]

## Project Overview

The system simulates a common industrial scenario where a raw sensor signal must be cleaned and monitored for failures in real-time. It uses a two-stage machine learning pipeline to achieve this:

1.  **Stage 1: ADC Corrector Model:** A Multi-Layer Perceptron (MLP) acts as a replacement for a traditional Look-Up Table (LUT), correcting non-linearities from the Analog-to-Digital Converter (ADC).
2.  **Stage 2: Anomaly Detection Model:** An LSTM Autoencoder, trained only on normal data, receives the corrected signal and identifies anomalies by detecting high reconstruction error.

The entire pipeline runs locally via a Python "agent," which then publishes the signal value and system status to a live web dashboard using a real-time messaging service.


## Features

- **Dual-ML Pipeline:** Sequentially combines a correction model and a detection model for higher accuracy.
- **Real-Time Processing:** The local agent processes and analyzes the signal with low latency.
- **Live Web Dashboard:** A deployed Next.js application visualizes the signal and system status for remote monitoring.
- **Optimized for Edge:** The models are designed to be quantized and exported to ONNX for efficient inference on edge hardware.
- **Dynamic Anomaly Threshold:** The system intelligently calculates an anomaly threshold based on the model's performance on normal data, avoiding hard-coded "magic numbers."

## Tech Stack

- **Machine Learning & Backend:**
  - Python
  - PyTorch & PyTorch Lightning
  - Scikit-learn, NumPy, Pandas
  - Ably (for real-time messaging)
- **Frontend:**
  - Next.js (React Framework)
  - Tailwind CSS
  - Vercel (for deployment)
- **DevOps & Infrastructure:**
  - Git & GitHub
  - Virtual Environments (`venv`)
  - Node Version Manager (`nvm`)

## Local Setup and Installation

### Prerequisites

- Python 3.9+
- An Ably API Key ([get one for free](https://ably.com/))
- Node.js (installed via `nvm` is recommended)



Clone the repository and set up the Python environment.
Create and activate a virtual environment

python -m venv venv
source venv/bin/activate
Install dependencies

pip install -r requirements.txt

## The ML agent repo is availaible at :
https://github.com/grizzleyyybear/ml_anomaly_detection



