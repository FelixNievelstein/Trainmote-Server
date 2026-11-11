import { z } from 'zod';

export const trainIdSchema = z.coerce.number().int().positive();

export const createTrainSchema = z
  .object({
    name: z.string().trim().min(1).max(100),
    address: z.number().int().min(1).max(9999),
  })
  .strict();

export const trainCommandSchema = z
  .object({
    action: z.enum(['start', 'stop']).optional(),
    speed: z.number().int().min(0).max(100).optional(),
    direction: z.enum(['forward', 'backward', 'stop']).optional(),
  })
  .strict()
  .refine((cmd) => Object.keys(cmd).length > 0, { message: 'At least one of action, speed, direction is required' });

export type CreateTrain = z.infer<typeof createTrainSchema>;
export type TrainCommandBody = z.infer<typeof trainCommandSchema>;
