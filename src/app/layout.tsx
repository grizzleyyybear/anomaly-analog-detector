import type { Metadata } from "next";
import "./globals.css";
import ErrorBoundary from "./components/ErrorBoundary";

export const metadata: Metadata = {
  title: "Anomaly Analog Detector | Real-Time Industrial Signal Monitoring",
  description:
    "Real-time anomaly detection dashboard powered by a dual-ML pipeline — ADC correction and LSTM autoencoder — for industrial sensor monitoring.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary>{children}</ErrorBoundary>
      </body>
    </html>
  );
}
