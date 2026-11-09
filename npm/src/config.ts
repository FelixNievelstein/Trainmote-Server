import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: Number(process.env.PORT ?? 3000),
  trainPowerPin: Number(process.env.TRAIN_POWER_PIN ?? 17),
};
