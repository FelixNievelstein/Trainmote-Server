import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/**/*.test.ts'],
    globalSetup: ['test/globalSetup.ts'],
    setupFiles: ['test/setupEnv.ts'],
    // Alle Testdateien teilen sich eine SQLite-Datei, daher nacheinander ausführen.
    fileParallelism: false,
  },
});
