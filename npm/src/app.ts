import express from 'express';
import cors from 'cors';
import type { PrismaClient } from '@prisma/client';
import { errorHandler, notFoundHandler } from './http/errors';
import type { GpioInterface } from './lib/gpio';
import type { TrainCommand, TrainContext } from './lib/trainMachine';

/** Der Teil des XState-Interpreters, den die App benötigt. */
export interface TrainService {
  send(event: TrainCommand): unknown;
  getSnapshot(): { value: unknown; context: TrainContext };
}

export interface AppDeps {
  prisma: PrismaClient;
  gpio: GpioInterface;
  service: TrainService;
}

export function createApp({ prisma, gpio, service }: AppDeps) {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get('/health', (_req, res) => {
    res.json({ ok: true, state: service.getSnapshot().value });
  });

  app.get('/api/trains', async (_req, res) => {
    const trains = await prisma.train.findMany();
    res.json(trains);
  });

  app.post('/api/trains', async (req, res) => {
    const { name, address } = req.body ?? {};

    if (!name || typeof address !== 'number') {
      res.status(400).json({ error: 'Missing name or address' });
      return;
    }

    const train = await prisma.train.create({
      data: {
        name,
        address,
        speed: 0,
        direction: 'stop',
        isActive: true,
      },
    });

    res.status(201).json(train);
  });

  app.post('/api/trains/:id/command', async (req, res) => {
    const { id } = req.params;
    const { action, speed, direction } = req.body ?? {};

    const trainId = Number(id);
    if (Number.isNaN(trainId)) {
      res.status(400).json({ error: 'Invalid train id' });
      return;
    }

    const current = await prisma.train.findUnique({ where: { id: trainId } });
    if (!current) {
      res.status(404).json({ error: 'Train not found' });
      return;
    }

    if (action === 'start') {
      service.send({ type: 'START' });
      gpio.init();
      gpio.setMode(17, 'output');
      gpio.write(17, 1);
    }

    if (action === 'stop') {
      service.send({ type: 'STOP' });
      gpio.write(17, 0);
    }

    if (typeof speed === 'number') {
      service.send({ type: 'SET_SPEED', value: speed });
    }

    if (direction === 'forward' || direction === 'backward' || direction === 'stop') {
      service.send({ type: 'SET_DIRECTION', value: direction });
    }

    const updated = await prisma.train.update({
      where: { id: trainId },
      data: {
        speed: typeof speed === 'number' ? speed : current.speed,
        direction: direction ?? current.direction,
        isActive: action !== 'stop',
      },
    });

    res.json({ ok: true, train: updated, machine: service.getSnapshot().context });
  });

  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
