import { NextRequest, NextResponse } from "next/server"
import { env } from "@/lib/env"

export async function POST(request: NextRequest) {
  const response = NextResponse.json({ success: true })

  // Clear the JWT cookie
  response.cookies.set(env.JWT_COOKIE_NAME, "", {
    httpOnly: true,
    path: "/",
    maxAge: 0,
    sameSite: "lax",
    secure: env.JWT_COOKIE_SECURE,
  })

  return response
}

