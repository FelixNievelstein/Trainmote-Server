import request from 'supertest';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { Prisma } from '@prisma/client';
import { toErrorResponse } from '../src/http/errors';
import { buildApp, prisma, resetDb } from './helpers';

beforeEach(resetDb);
afterAll(() => prisma.$disconnect());

describe('Fehlerbehandlung', () => {
  it('beantwortet den Absturzfall aus dem Review mit 400', async () => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains').send({ name: { x: 1 }, address: 1 });
    expect(res.status).toBe(400);

    // Der Server antwortet weiterhin.
    expect((await request(app).get('/health')).status).toBe(200);
  });

  it('beantwortet kaputtes JSON mit 400 und JSON-Fehler', async () => {
    const { app } = buildApp();
    const res = await request(app)
      .post('/api/trains')
      .set('Content-Type', 'application/json')
      .send('{"name": ');
    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: 'Invalid JSON' });
  });

  it('beantwortet unbekannte Routen mit 404 als JSON', async () => {
    const { app } = buildApp();
    const res = await request(app).get('/gibt-es-nicht');
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: 'Not found' });
  });
});

describe('toErrorResponse', () => {
  const meta = { clientVersion: 'test' };

  it('bildet Prisma-Fehler auf 400 bzw. 404 ab', () => {
    expect(toErrorResponse(new Prisma.PrismaClientValidationError('x', meta)).status).toBe(400);
    const notFound = new Prisma.PrismaClientKnownRequestError('x', { ...meta, code: 'P2025' });
    expect(toErrorResponse(notFound).status).toBe(404);
  });

  it('gibt bei unbekannten Fehlern keine Details preis', () => {
    expect(toErrorResponse(new Error('geheim'))).toEqual({ status: 500, message: 'Internal server error' });
  });
});
