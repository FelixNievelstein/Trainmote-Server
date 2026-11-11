import { createMachine, assign } from 'xstate';

export type Direction = 'forward' | 'backward' | 'stop';

export type TrainCommand =
  | { type: 'START' }
  | { type: 'STOP' }
  | { type: 'SET_SPEED'; value: number }
  | { type: 'SET_DIRECTION'; value: Direction };

export type TrainContext = {
  speed: number;
  direction: Direction;
};

const clampSpeed = (value: number): number => Math.max(0, Math.min(100, value));

export const trainMachine = createMachine<TrainContext, TrainCommand>({
  id: 'train',
  predictableActionArguments: true,
  context: {
    speed: 0,
    direction: 'stop',
  },
  initial: 'idle',
  states: {
    idle: {
      on: {
        START: { target: 'running', actions: assign({ speed: 20 }) },
        SET_SPEED: { actions: assign({ speed: (_ctx, event) => clampSpeed(event.value) }) },
        SET_DIRECTION: { actions: assign({ direction: (_ctx, event) => event.value }) },
      },
    },
    running: {
      on: {
        STOP: { target: 'idle', actions: assign({ speed: 0, direction: 'stop' as Direction }) },
        SET_SPEED: { actions: assign({ speed: (_ctx, event) => clampSpeed(event.value) }) },
        SET_DIRECTION: { actions: assign({ direction: (_ctx, event) => event.value }) },
      },
    },
  },
});
