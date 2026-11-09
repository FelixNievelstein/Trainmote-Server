import { createMachine, assign } from 'xstate';

export type TrainCommand =
  | { type: 'START' }
  | { type: 'STOP' }
  | { type: 'SET_SPEED'; value: number }
  | { type: 'SET_DIRECTION'; value: 'forward' | 'backward' | 'stop' };

export type TrainContext = {
  speed: number;
  direction: 'forward' | 'backward' | 'stop';
};

export const trainMachine = createMachine({
  id: 'train',
  context: {
    speed: 0,
    direction: 'stop' as const,
  },
  initial: 'idle',
  states: {
    idle: {
      on: {
        START: { target: 'running', actions: assign({ speed: 20 }) },
        SET_SPEED: { actions: assign({ speed: (_ctx, event) => Math.max(0, Math.min(100, event.value)) }) },
        SET_DIRECTION: { actions: assign({ direction: (_ctx, event) => event.value }) },
      },
    },
    running: {
      on: {
        STOP: { target: 'idle', actions: assign({ speed: 0, direction: 'stop' }) },
        SET_SPEED: { actions: assign({ speed: (_ctx, event) => Math.max(0, Math.min(100, event.value)) }) },
        SET_DIRECTION: { actions: assign({ direction: (_ctx, event) => event.value }) },
      },
    },
  },
});

export type TrainMachineState = typeof trainMachine;
