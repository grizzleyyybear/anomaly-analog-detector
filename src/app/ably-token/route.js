// src/app/api/ably-token/route.js

import Ably from "ably";

export async function GET(request) {
  // This code runs only on the server, where it can safely access environment variables.
  const client = new Ably.Realtime({ key: process.env.ABLY_API_KEY });
  
  // Create a temporary, safe token for the frontend client.
  const tokenRequestData = await client.auth.createTokenRequest({ clientId: 'anomaly-dashboard-client' });
  
  return Response.json(tokenRequestData);
}
