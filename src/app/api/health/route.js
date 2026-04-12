import { readFileSync } from 'fs';
import { join } from 'path';

let pkg;
try {
  pkg = JSON.parse(readFileSync(join(process.cwd(), 'package.json'), 'utf-8'));
} catch {
  pkg = { name: 'anomaly-dashboard', version: 'unknown' };
}

const startTime = Date.now();

export async function GET() {
  return Response.json({
    status: 'healthy',
    service: pkg.name,
    version: pkg.version,
    uptime: Math.floor((Date.now() - startTime) / 1000),
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    ably: process.env.ABLY_API_KEY ? 'configured' : 'missing',
  });
}
