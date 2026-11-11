import request from 'supertest';
import { afterAll, beforeEach, describe, expect, it } from 'vitest';
import { buildApp, prisma, resetDb } from './helpers';

beforeEach(resetDb);
afterAll(() => prisma.$disconnect());

describe('Fehlerbehandlung', () => {
  it('beantwortet einen Datenbank-Validierungsfehler mit 400, statt abzustürzen', async () => {
    const { app } = buildApp();
    const res = await request(app).post('/api/trains').send({ name: { x: 1 }, address: 1 });
    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: 'Invalid request data' });

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
