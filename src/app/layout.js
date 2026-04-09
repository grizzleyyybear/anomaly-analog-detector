import "./globals.css";

export const metadata = {
  title: "Anomaly Analog Detector | Real-Time Industrial Signal Monitoring",
  description:
    "Real-time anomaly detection dashboard powered by a dual-ML pipeline — ADC correction and LSTM autoencoder — for industrial sensor monitoring.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
