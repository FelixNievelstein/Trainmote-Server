import request from 'supertest';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { buildApp, prisma, resetDb } from './helpers';

beforeEach(resetDb);
afterAll(() => prisma.$disconnect());

async function createTrain() {
  const { app } = buildApp();
  const { body } = await request(app).post('/api/trains').send({ name: 'ICE', address: 3 });
  return { app, id: body.id as number };
}

describe('POST /api/trains Validierung', () => {
  it.each([
    [{ name: '', address: 3 }],
    [{ name: 'ICE', address: 0 }],
    [{ name: 'ICE', address: 1.5 }],
    [{ name: 'ICE', address: '3' }],
    [{ name: 'ICE', address: 3, extra: true }],
  ])('lehnt %j mit 400 ab', async (body) => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains').send(body);
    expect(res.status).toBe(400);
    expect(typeof res.body.error).toBe('string');
  });
});

describe('POST /api/trains/:id/command Validierung', () => {
  it.each([
    [{ speed: 500 }],
    [{ speed: -1 }],
    [{ speed: 1.5 }],
    [{ direction: 'sideways' }],
    [{ action: 'jump' }],
    [{}],
  ])('lehnt %j mit 400 ab und speichert nichts', async (body) => {
    const { app, id } = await createTrain();
    const res = await request(app).post(`/api/trains/${id}/command`).send(body);
    expect(res.status).toBe(400);
    const train = await prisma.train.findUniqueOrThrow({ where: { id } });
    expect(train).toMatchObject({ speed: 0, direction: 'stop' });
  });

  it('lehnt eine ungültige ID mit 400 ab', async () => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains/abc/command').send({ action: 'start' });
    expect(res.status).toBe(400);
  });

  it('übernimmt gültige Werte', async () => {
    const { app, id } = await createTrain();
    const res = await request(app).post(`/api/trains/${id}/command`).send({ speed: 50, direction: 'forward' });
    expect(res.status).toBe(200);
    expect(res.body.train).toMatchObject({ speed: 50, direction: 'forward' });
  });
});
