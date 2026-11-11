import type { RequestHandler } from 'express';
import type { ZodError, ZodTypeAny, z } from 'zod';
import { HttpError } from './errors';

export function formatZodError(error: ZodError): string {
  return error.issues
    .map((issue) => (issue.path.length > 0 ? `${issue.path.join('.')}: ${issue.message}` : issue.message))
    .join('; ');
}

/** Prüft einen Wert gegen ein Schema und wirft bei Fehlern HttpError 400. */
export function parseOrThrow<S extends ZodTypeAny>(schema: S, value: unknown): z.infer<S> {
  const result = schema.safeParse(value);
  if (!result.success) {
    throw new HttpError(400, formatZodError(result.error));
  }
  return result.data;
}

/** Middleware: ersetzt req.body durch die validierten Daten. */
export function validateBody(schema: ZodTypeAny): RequestHandler {
  return (req, _res, next) => {
    req.body = parseOrThrow(schema, req.body);
    next();
  };
}
