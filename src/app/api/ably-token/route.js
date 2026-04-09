import Ably from "ably";

export async function GET() {
  const apiKey = process.env.ABLY_API_KEY;

  if (!apiKey) {
    return Response.json(
      { error: "ABLY_API_KEY is not configured" },
      { status: 500 }
    );
  }

  try {
    const client = new Ably.Realtime({ key: apiKey });
    const tokenRequestData = await client.auth.createTokenRequest({
      clientId: "anomaly-dashboard-client",
    });
    client.close();
    return Response.json(tokenRequestData);
  } catch {
    return Response.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
