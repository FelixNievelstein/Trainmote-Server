export interface ShutdownStep {
  name: string;
  run: () => void | Promise<void>;
}

export interface ShutdownOptions {
  timeoutMs?: number;
  exit?: (code: number) => void;
  log?: (message: string, error?: unknown) => void;
}

/**
 * Erzeugt eine idempotente Shutdown-Funktion. Die Schritte laufen nacheinander;
 * ein fehlschlagender Schritt hält die übrigen nicht auf. Dauert alles länger
 * als timeoutMs, wird der Prozess mit Code 1 beendet.
 */
export function createShutdown(steps: ShutdownStep[], options: ShutdownOptions = {}) {
  const { timeoutMs = 5000, exit = (code) => process.exit(code), log = console.log } = options;
  let running: Promise<void> | undefined;

  return function shutdown(reason: string, exitCode = 0): Promise<void> {
    if (running) return running;

    running = (async () => {
      log(`Shutting down (${reason})`);
      const timer = setTimeout(() => {
        log(`Shutdown did not finish within ${timeoutMs} ms, forcing exit`);
        exit(1);
      }, timeoutMs);
      timer.unref?.();

      let failed = false;
      for (const step of steps) {
        try {
          await step.run();
        } catch (error) {
          failed = true;
          log(`Shutdown step "${step.name}" failed`, error);
        }
      }

      clearTimeout(timer);
      exit(failed && exitCode === 0 ? 1 : exitCode);
    })();

    return running;
  };
}
