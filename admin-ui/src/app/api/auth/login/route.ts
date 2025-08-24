import { NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import { env } from "@/lib/env"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    // Mock authentication - accept the credentials from the requirements
    if (email === "arun@slotifyme.com" && password === "admin123") {
      // Create a mock JWT token
      const mockToken = "mock-jwt-token-" + Date.now()

      // Set the JWT cookie
      const cookieStore = await cookies()
      cookieStore.set(env.JWT_COOKIE_NAME, mockToken, {
        httpOnly: true,
        secure: env.JWT_COOKIE_SECURE,
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: "/",
      })

      return NextResponse.json({
        success: true,
        message: "Login successful",
        user: {
          email: "arun@slotifyme.com",
          name: "Arun",
          role: "admin",
        },
      })
    } else {
      return NextResponse.json(
        { success: false, message: "Invalid credentials" },
        { status: 401 }
      )
    }
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json(
      { success: false, message: "Internal server error" },
      { status: 500 }
    )
  }
}
