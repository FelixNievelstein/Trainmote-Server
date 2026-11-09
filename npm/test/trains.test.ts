import request from 'supertest';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { buildApp, prisma, resetDb } from './helpers';

beforeEach(resetDb);
afterAll(() => prisma.$disconnect());

describe('GET /health', () => {
  it('meldet ok und den Zustand der Maschine', async () => {
    const { app } = buildApp();
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ ok: true, state: 'idle' });
  });
});

describe('/api/trains', () => {
  it('legt einen Zug an und listet ihn auf', async () => {
    const { app } = buildApp();
    const created = await request(app).post('/api/trains').send({ name: 'ICE', address: 3 });
    expect(created.status).toBe(201);
    expect(created.body).toMatchObject({ name: 'ICE', address: 3, speed: 0, direction: 'stop' });

    const list = await request(app).get('/api/trains');
    expect(list.status).toBe(200);
    expect(list.body).toHaveLength(1);
  });

  it('lehnt fehlende Felder mit 400 ab', async () => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains').send({ name: 'ICE' });
    expect(res.status).toBe(400);
  });
});

describe('POST /api/trains/:id/command', () => {
  it('start schaltet GPIO 17 an, stop wieder aus', async () => {
    const { app, gpio } = buildApp();
    const { body: train } = await request(app).post('/api/trains').send({ name: 'ICE', address: 3 });

    const started = await request(app).post(`/api/trains/${train.id}/command`).send({ action: 'start' });
    expect(started.status).toBe(200);
    expect(gpio.read(17)).toBe(1);

    const stopped = await request(app).post(`/api/trains/${train.id}/command`).send({ action: 'stop' });
    expect(stopped.body.train.isActive).toBe(false);
    expect(gpio.read(17)).toBe(0);
  });

  it('liefert 404 für unbekannte Züge', async () => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains/999/command').send({ action: 'start' });
    expect(res.status).toBe(404);
  });
});
