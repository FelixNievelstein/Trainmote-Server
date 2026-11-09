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
  const service = interpret(trainMachine).start();
  const app = createApp({ prisma, gpio, service });
  return { app, gpio, service };
}
