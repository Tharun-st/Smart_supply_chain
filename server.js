/**
 * Intelligent Supply Chain Management System
 * Production HTTP Server & Python Flask Runner
 * 
 * Provides:
 *   - Fast HTTP Server listening on port 5000 (http://localhost:5000)
 *   - Direct high-speed static asset serving from /static/
 *   - Persistent Python worker executing custom Data Structures & Algorithms
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = process.env.PORT || 5000;
const PYTHON_PATH = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
const BRIDGE_PATH = path.join(__dirname, 'bridge.py');

// MIME types for static asset serving
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// Spawn persistent Python worker process
console.log('[Server] Spawning persistent Python Flask & DSA engine...');
const pyWorker = spawn(PYTHON_PATH, ['-u', BRIDGE_PATH], {
  cwd: __dirname,
  stdio: ['pipe', 'pipe', 'inherit']
});

let requestQueue = [];
let isProcessing = false;
let responseBuffer = '';

// Handle stdout line from Python worker
pyWorker.stdout.on('data', (chunk) => {
  responseBuffer += chunk.toString();
  const lines = responseBuffer.split('\n');
  responseBuffer = lines.pop(); // keep remainder

  for (const line of lines) {
    if (line.trim()) {
      try {
        const resData = JSON.parse(line);
        const currentReq = requestQueue.shift();
        if (currentReq) {
          currentReq.resolve(resData);
        }
      } catch (e) {
        console.error('[Server] Failed to parse Python response JSON:', e);
      }
    }
  }
});

pyWorker.on('error', (err) => {
  console.error('[Server] Python worker error:', err);
  while (requestQueue.length > 0) {
    const req = requestQueue.shift();
    req.reject(err);
  }
});

pyWorker.on('exit', (code) => {
  console.log(`[Server] Python worker exited with code ${code}`);
  while (requestQueue.length > 0) {
    const req = requestQueue.shift();
    req.reject(new Error(`Python worker exited with code ${code}`));
  }
});

function forwardToPython(method, urlPath, body, headers) {
  return new Promise((resolve, reject) => {
    requestQueue.push({ resolve, reject });
    const payload = JSON.stringify({
      method,
      path: urlPath,
      body: body || null,
      headers: headers || {}
    }) + '\n';
    pyWorker.stdin.write(payload);
  });
}

// Create HTTP Server
const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  const pathname = parsedUrl.pathname;

  // 1. Static file serving (/static/...)
  if (pathname.startsWith('/static/')) {
    const relativePath = pathname.substring(1); // remove leading slash
    const filePath = path.join(__dirname, relativePath);
    const ext = path.extname(filePath).toLowerCase();

    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Static file not found');
      } else {
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';
        res.writeHead(200, {
          'Content-Type': contentType,
          'Cache-Control': 'public, max-age=3600'
        });
        res.end(data);
      }
    });
    return;
  }

  // 2. Collect request body for POST / PUT
  let bodyBuffer = '';
  req.on('data', (chunk) => {
    bodyBuffer += chunk.toString();
  });

  req.on('end', async () => {
    let parsedBody = null;
    if (bodyBuffer) {
      try {
        parsedBody = JSON.parse(bodyBuffer);
      } catch (e) {
        parsedBody = bodyBuffer;
      }
    }

    try {
      // Forward request to Flask and custom DSA engine in Python
      const pyResp = await forwardToPython(req.method, req.url, parsedBody, req.headers);
      
      res.writeHead(pyResp.status, {
        'Content-Type': pyResp.content_type || 'application/json'
      });
      res.end(pyResp.body);
    } catch (err) {
      console.error('[Server Error]', err);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'error', message: err.message }));
    }
  });
});

server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`[Server Error] Port ${PORT} is already in use. Please terminate existing instances on port ${PORT}.`);
    process.exit(1);
  } else {
    console.error('[Server Error]', e);
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('====================================================================');
  console.log('  INTELLIGENT SUPPLY CHAIN MANAGEMENT SYSTEM');
  console.log('  Academic Data Structures & Algorithmic Problem Solving Project');
  console.log(`  Live URL: http://127.0.0.1:${PORT}`);
  console.log('====================================================================');
});
