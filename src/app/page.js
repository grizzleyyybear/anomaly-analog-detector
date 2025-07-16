// src/app/page.js
'use client';

import { useState, useEffect } from 'react';
import { Realtime } from 'ably';

export default function Home() {
  const [signalValue, setSignalValue] = useState(0);
  const [anomalyStatus, setAnomalyStatus] = useState('Normal');

  useEffect(() => {
    
    const ABLY_API_KEY = 'zmmFew.Ar9xMg:JHpKZPm5YoWuFqaS3tNw1OpDA4aN_7q1zoPl6ALRkic';

    const ably = new Realtime({ key: ABLY_API_KEY });
    const signalChannel = ably.channels.get('signal-channel');
    const anomalyChannel = ably.channels.get('anomaly-channel');

    signalChannel.subscribe((message) => {
      setSignalValue(message.data.value.toFixed(4));
    });

    anomalyChannel.subscribe((message) => {
      setAnomalyStatus(message.data.status);
    });

    // Cleanup on component unmount
    return () => {
      signalChannel.unsubscribe();
      anomalyChannel.unsubscribe();
      ably.close();
    };
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Real-Time Signal Monitor</h1>
        <p className="text-lg text-gray-400 mb-8">Receiving live data from the local agent...</p>
        
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <p className="text-xl mb-2">Current Signal Value</p>
          <p className="text-6xl font-mono font-bold text-cyan-400">{signalValue}</p>
        </div>

        <div className={`rounded-lg p-6 ${anomalyStatus === 'Anomaly Detected' ? 'bg-red-500' : 'bg-green-500'}`}>
          <p className="text-xl mb-2">System Status</p>
          <p className="text-4xl font-bold">{anomalyStatus}</p>
        </div>
      </div>
    </main>
  );
}
