'use client';

import { useState, useEffect, useRef } from 'react';
import { Realtime } from 'ably';
import type { TokenParams, TokenRequest, ErrorInfo } from 'ably';

const MAX_HISTORY = 200;
const MAX_LOG = 50;

export interface SignalPoint {
  time: string;
  value: number;
  timestamp: string;
  raw: number | null;
  corrected: number | string;
}

export interface AnomalyEntry {
  status: string;
  timestamp: string;
  time: string;
  reconstructionError: number | null;
  threshold: number | null;
}

export interface PipelineInfo {
  stage1: string;
  stage2: string;
}

export interface UseAblyReturn {
  connectionStatus: string;
  signalHistory: SignalPoint[];
  currentSignal: SignalPoint | null;
  anomalyStatus: AnomalyEntry;
  anomalyLog: AnomalyEntry[];
  pipelineInfo: PipelineInfo;
  reconstructionError: number | null;
  threshold: number | null;
}

export function useAbly(): UseAblyReturn {
  const [connectionStatus, setConnectionStatus] = useState<string>('connecting');
  const [signalHistory, setSignalHistory] = useState<SignalPoint[]>([]);
  const [currentSignal, setCurrentSignal] = useState<SignalPoint | null>(null);
  const [anomalyStatus, setAnomalyStatus] = useState<AnomalyEntry>({
    status: 'Waiting...', timestamp: '', time: '', reconstructionError: null, threshold: null,
  });
  const [anomalyLog, setAnomalyLog] = useState<AnomalyEntry[]>([]);
  const [pipelineInfo, setPipelineInfo] = useState<PipelineInfo>({ stage1: 'idle', stage2: 'idle' });
  const [reconstructionError, setReconstructionError] = useState<number | null>(null);
  const [threshold, setThreshold] = useState<number | null>(null);
  const ablyRef = useRef<Realtime | null>(null);

  useEffect(() => {
    const authCallback = (
      tokenParams: TokenParams,
      callback: (error: ErrorInfo | string | null, tokenOrDetails: TokenRequest | string | null) => void,
    ) => {
      fetch('/api/ably-token')
        .then(res => {
          if (!res.ok) throw new Error(`Token fetch failed: ${res.status}`);
          return res.json();
        })
        .then(tokenRequest => callback(null, tokenRequest))
        .catch(err => callback(err, null));
    };

    const ably = new Realtime({ authCallback });
    ablyRef.current = ably;

    ably.connection.on('connected', () => setConnectionStatus('connected'));
    ably.connection.on('disconnected', () => setConnectionStatus('disconnected'));
    ably.connection.on('suspended', () => setConnectionStatus('suspended'));
    ably.connection.on('failed', () => setConnectionStatus('failed'));
    ably.connection.on('connecting', () => setConnectionStatus('connecting'));

    const signalChannel = ably.channels.get('signal-channel');
    const anomalyChannel = ably.channels.get('anomaly-channel');

    signalChannel.subscribe((message) => {
      const data = message.data;
      const value = typeof data === 'object' ? data.value : data;
      const timestamp = data?.timestamp || new Date().toISOString();

      const point: SignalPoint = {
        time: new Date(timestamp).toLocaleTimeString(),
        value: parseFloat(value),
        timestamp,
        raw: data?.rawValue ?? null,
        corrected: data?.correctedValue ?? value,
      };

      setCurrentSignal(point);
      setSignalHistory(prev => {
        const next = [...prev, point];
        return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next;
      });

      if (data?.stage1Status) {
        setPipelineInfo(prev => ({ ...prev, stage1: data.stage1Status }));
      }
    });

    anomalyChannel.subscribe((message) => {
      const data = message.data;
      const status = typeof data === 'object' ? data.status : data;
      const timestamp = data?.timestamp || new Date().toISOString();

      const entry: AnomalyEntry = {
        status,
        timestamp,
        time: new Date(timestamp).toLocaleTimeString(),
        reconstructionError: data?.reconstructionError ?? null,
        threshold: data?.threshold ?? null,
      };

      setAnomalyStatus(entry);
      setAnomalyLog(prev => {
        const next = [entry, ...prev];
        return next.length > MAX_LOG ? next.slice(0, MAX_LOG) : next;
      });

      if (data?.reconstructionError != null) setReconstructionError(data.reconstructionError);
      if (data?.threshold != null) setThreshold(data.threshold);
      if (data?.stage2Status) setPipelineInfo(prev => ({ ...prev, stage2: data.stage2Status }));
    });

    return () => {
      signalChannel.unsubscribe();
      anomalyChannel.unsubscribe();
      ably.close();
    };
  }, []);

  return {
    connectionStatus,
    signalHistory,
    currentSignal,
    anomalyStatus,
    anomalyLog,
    pipelineInfo,
    reconstructionError,
    threshold,
  };
}
