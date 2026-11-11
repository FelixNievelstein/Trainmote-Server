// Wird vor jeder Testdatei geladen, bevor ein PrismaClient entsteht.
process.env.DATABASE_URL = 'file:./test.db';
