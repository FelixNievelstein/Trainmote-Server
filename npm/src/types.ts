export type Direction = 'forward' | 'backward' | 'stop';

export interface TrainStateDto {
  id: number;
  name: string;
  address: number;
  speed: number;
  direction: Direction;
  isActive: boolean;
}

export interface WebSocketMessage {
  type: 'status' | 'command' | 'error';
  payload?: unknown;
}
