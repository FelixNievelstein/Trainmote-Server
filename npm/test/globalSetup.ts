import { execSync } from 'node:child_process';
import { rmSync } from 'node:fs';
import path from 'node:path';

const dbFile = path.join(__dirname, '..', 'prisma', 'test.db');

export function setup() {
  rmSync(dbFile, { force: true });
  execSync('npx prisma db push --skip-generate', {
    env: { ...process.env, DATABASE_URL: 'file:./test.db' },
    stdio: 'ignore',
  });
}

export function teardown() {
  rmSync(dbFile, { force: true });
  rmSync(`${dbFile}-journal`, { force: true });
}
