import { Prisma } from '@prisma/client';
import type { ErrorRequestHandler, RequestHandler } from 'express';

/** Fehler mit HTTP-Status, dessen Meldung an den Client gehen darf. */
export class HttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'HttpError';
  }
}

interface ErrorResponse {
  status: number;
  message: string;
}

function hasStatus(err: unknown): err is { status: number; type?: string; message: string } {
  return typeof err === 'object' && err !== null && typeof (err as { status?: unknown }).status === 'number';
}

export function toErrorResponse(err: unknown): ErrorResponse {
  if (err instanceof HttpError) {
    return { status: err.status, message: err.message };
  }
  if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === 'P2025') {
    return { status: 404, message: 'Not found' };
  }
  if (err instanceof Prisma.PrismaClientValidationError) {
    return { status: 400, message: 'Invalid request data' };
  }
  // Fehler von body-parser (z. B. kaputtes JSON, zu großer Body)
  if (hasStatus(err) && err.status >= 400 && err.status < 500) {
    const message = err.type === 'entity.parse.failed' ? 'Invalid JSON' : err.message;
    return { status: err.status, message };
  }
  return { status: 500, message: 'Internal server error' };
}

export const notFoundHandler: RequestHandler = (_req, _res, next) => {
  next(new HttpError(404, 'Not found'));
};

export const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  const { status, message } = toErrorResponse(err);
  if (status >= 500) {
    console.error(`${req.method} ${req.originalUrl} failed:`, err);
  }
  res.status(status).json({ error: message });
};
