import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function createServer() {
  const app = express();

  // Create Vite server in middleware mode
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
    root: __dirname,
    publicDir: 'public',
  });

  app.use(vite.ssrFixStacktrace);
  app.use(vite.middlewares);

  app.listen(5173, () => {
    console.log('Server running at http://localhost:5173');
  });
}

createServer().catch(console.error);