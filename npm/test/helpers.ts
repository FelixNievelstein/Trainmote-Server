import { PrismaClient } from '@prisma/client';
import { interpret } from 'xstate';
import { createApp } from '../src/app';
import { createGpio } from '../src/lib/gpio';
import { trainMachine } from '../src/lib/trainMachine';

export const prisma = new PrismaClient();

export async function resetDb() {
  await prisma.train.deleteMany();
  await prisma.route.deleteMany();
}

export function buildApp() {
  const gpio = createGpio();
  gpio.init();
  gpio.setMode(17, 'output');
  const service = interpret(trainMachine).start();
  const app = createApp({ prisma, gpio, service, trainPowerPin: 17 });
  return { app, gpio, service };
}
