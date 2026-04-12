'use client';

import { useState, useEffect, useRef } from 'react';
import { Realtime } from 'ably';

const MAX_HISTORY = 200;
const MAX_LOG = 50;

export function useAbly() {
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [signalHistory, setSignalHistory] = useState([]);
  const [currentSignal, setCurrentSignal] = useState(null);
  const [anomalyStatus, setAnomalyStatus] = useState({ status: 'Waiting...', timestamp: null });
  const [anomalyLog, setAnomalyLog] = useState([]);
  const [pipelineInfo, setPipelineInfo] = useState({ stage1: 'idle', stage2: 'idle' });
  const [reconstructionError, setReconstructionError] = useState(null);
  const [threshold, setThreshold] = useState(null);
  const ablyRef = useRef(null);

  useEffect(() => {
    const authCallback = (tokenParams, callback) => {
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

      const point = {
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

      const entry = {
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
