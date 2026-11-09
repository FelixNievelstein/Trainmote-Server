export type PinMode = 'input' | 'output';

export interface GpioInterface {
  init(): void;
  setMode(pin: number, mode: PinMode): void;
  write(pin: number, value: 0 | 1): void;
  read(pin: number): number;
  close(): void;
}

class MockGpio implements GpioInterface {
  private pins = new Map<number, 0 | 1>();

  init(): void {
    // no-op for local development on Mac
  }

  setMode(pin: number, mode: PinMode): void {
    void pin;
    void mode;
  }

  write(pin: number, value: 0 | 1): void {
    this.pins.set(pin, value);
  }

  read(pin: number): number {
    return this.pins.get(pin) ?? 0;
  }

  close(): void {
    this.pins.clear();
  }
}

export const gpio: GpioInterface = new MockGpio();

export const createGpio = (): GpioInterface => new MockGpio();
