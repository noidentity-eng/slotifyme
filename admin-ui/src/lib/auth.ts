import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { env } from "./env"

export async function getTokenFromCookies(): Promise<string | null> {
  const cookieStore = await cookies()
  return cookieStore.get(env.JWT_COOKIE_NAME)?.value || null
}

export async function requireAuth(): Promise<void> {
  const token = await getTokenFromCookies()
  if (!token) {
    redirect("/login")
  }
}

export async function logout(): Promise<void> {
  const cookieStore = await cookies()
  cookieStore.delete(env.JWT_COOKIE_NAME)
  redirect("/login")
}
