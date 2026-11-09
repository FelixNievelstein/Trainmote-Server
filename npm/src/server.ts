import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { interpret } from 'xstate';
import { config } from './config';
import { prisma } from './lib/prisma';
import { gpio } from './lib/gpio';
import { trainMachine } from './lib/trainMachine';
import { createApp } from './app';

const service = interpret(trainMachine).start();
const app = createApp({ prisma, gpio, service });
const httpServer = createServer(app);
const wss = new WebSocketServer({ server: httpServer, path: '/ws' });

wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'status', payload: { state: service.getSnapshot().value } }));

  ws.on('message', (raw) => {
    try {
      const message = JSON.parse(raw.toString()) as { type?: string; payload?: unknown };
      if (message.type === 'command') {
        service.send({ type: 'START' });
      }
      ws.send(JSON.stringify({ type: 'status', payload: { state: service.getSnapshot().value } }));
    } catch (error) {
      const err = error as Error;
      ws.send(JSON.stringify({ type: 'error', payload: { message: err.message } }));
    }
  });
});

httpServer.listen(config.port, () => {
  console.log(`Trainmote server listening on http://localhost:${config.port}`);
});

process.on('SIGINT', async () => {
  service.stop();
  gpio.close();
  await prisma.$disconnect();
  process.exit(0);
});
