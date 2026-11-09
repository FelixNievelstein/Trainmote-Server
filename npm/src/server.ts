import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { interpret } from 'xstate';
import { config } from './config';
import { prisma } from './lib/prisma';
import { gpio } from './lib/gpio';
import { trainMachine } from './lib/trainMachine';
import { createApp } from './app';
import { createShutdown } from './shutdown';

gpio.init();
gpio.setMode(config.trainPowerPin, 'output');
gpio.write(config.trainPowerPin, 0);

const service = interpret(trainMachine).start();
const app = createApp({ prisma, gpio, service, trainPowerPin: config.trainPowerPin });
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

const shutdown = createShutdown([
  {
    name: 'http',
    run: () =>
      new Promise<void>((resolve) => {
        httpServer.close(() => resolve());
        httpServer.closeAllConnections();
      }),
  },
  {
    name: 'websocket',
    run: () => {
      wss.clients.forEach((client) => client.terminate());
      wss.close();
    },
  },
  { name: 'state machine', run: () => void service.stop() },
  {
    name: 'gpio',
    run: () => {
      gpio.write(config.trainPowerPin, 0);
      gpio.close();
    },
  },
  { name: 'database', run: () => prisma.$disconnect() },
]);

httpServer.listen(config.port, () => {
  console.log(`Trainmote server listening on http://localhost:${config.port}`);
});

process.on('SIGINT', () => void shutdown('SIGINT'));
process.on('SIGTERM', () => void shutdown('SIGTERM'));

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled promise rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  void shutdown('uncaughtException', 1);
});
