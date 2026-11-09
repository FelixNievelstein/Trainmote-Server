import { describe, expect, it, vi } from 'vitest';
import { createShutdown } from '../src/shutdown';

const silent = () => {};

describe('createShutdown', () => {
  it('führt alle Schritte in Reihenfolge aus und beendet mit Code 0', async () => {
    const calls: string[] = [];
    const exit = vi.fn();
    const shutdown = createShutdown(
      [
        { name: 'a', run: () => void calls.push('a') },
        { name: 'b', run: async () => void calls.push('b') },
      ],
      { exit, log: silent },
    );

    await shutdown('test');
    expect(calls).toEqual(['a', 'b']);
    expect(exit).toHaveBeenCalledWith(0);
  });

  it('läuft bei mehrfachem Aufruf nur einmal', async () => {
    const step = vi.fn();
    const exit = vi.fn();
    const shutdown = createShutdown([{ name: 'a', run: step }], { exit, log: silent });

    await Promise.all([shutdown('SIGINT'), shutdown('SIGTERM')]);
    expect(step).toHaveBeenCalledTimes(1);
    expect(exit).toHaveBeenCalledTimes(1);
  });

  it('setzt nach einem fehlerhaften Schritt fort und beendet mit Code 1', async () => {
    const after = vi.fn();
    const exit = vi.fn();
    const shutdown = createShutdown(
      [
        { name: 'kaputt', run: () => { throw new Error('x'); } },
        { name: 'danach', run: after },
      ],
      { exit, log: silent },
    );

    await shutdown('test');
    expect(after).toHaveBeenCalled();
    expect(exit).toHaveBeenCalledWith(1);
  });

  it('erzwingt nach dem Timeout das Beenden', async () => {
    vi.useFakeTimers();
    const exit = vi.fn();
    const shutdown = createShutdown([{ name: 'hängt', run: () => new Promise<void>(() => {}) }], {
      exit,
      log: silent,
      timeoutMs: 100,
    });

    void shutdown('test');
    await vi.advanceTimersByTimeAsync(100);
    expect(exit).toHaveBeenCalledWith(1);
    vi.useRealTimers();
  });
});
