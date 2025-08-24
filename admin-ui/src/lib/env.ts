import { z } from "zod"

const envSchema = z.object({
  NEXT_PUBLIC_APP_NAME: z.string().default("Slotifyme Admin"),
  BFF_BASE_URL: z.string().url().default("http://localhost:8100"),
  JWT_COOKIE_NAME: z.string().default("slotifyme_admin_jwt"),
  JWT_COOKIE_SECURE: z
    .enum(["true", "false"])
    .default("false")
    .transform((val) => val === "true"),
  PUBLIC_HOST_DOMAIN: z.string().default("slotifyme.com"),
})

export const env = envSchema.parse({
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  BFF_BASE_URL: process.env.BFF_BASE_URL,
  JWT_COOKIE_NAME: process.env.JWT_COOKIE_NAME,
  JWT_COOKIE_SECURE: process.env.JWT_COOKIE_SECURE,
  PUBLIC_HOST_DOMAIN: process.env.PUBLIC_HOST_DOMAIN,
})
