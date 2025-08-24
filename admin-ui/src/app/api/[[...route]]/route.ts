import { NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import { env } from "@/lib/env"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ route?: string[] }> }
) {
  const resolvedParams = await params
  return handleRequest(request, resolvedParams.route || [], "GET")
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ route?: string[] }> }
) {
  const resolvedParams = await params
  return handleRequest(request, resolvedParams.route || [], "POST")
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ route?: string[] }> }
) {
  const resolvedParams = await params
  return handleRequest(request, resolvedParams.route || [], "PUT")
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ route?: string[] }> }
) {
  const resolvedParams = await params
  return handleRequest(request, resolvedParams.route || [], "DELETE")
}

async function handleRequest(
  request: NextRequest,
  route: string[],
  method: string
) {
  const path = route?.join("/") || ""

  // Skip routes that have dedicated endpoints
  if (
    path.startsWith("auth/login") ||
    path.startsWith("admin/plans") ||
    path.startsWith("admin/addons") ||
    path.startsWith("admin/tenants")
  ) {
    return NextResponse.json(
      { error: `Use /api/${path} endpoint` },
      { status: 404 }
    )
  }

  const url = new URL(request.url)
  const targetUrl = `${env.BFF_BASE_URL}/${path}${url.search}`

  const headers = new Headers()

  // Copy relevant headers from the original request
  const contentType = request.headers.get("content-type")
  if (contentType) {
    headers.set("content-type", contentType)
  }

  // Handle authentication
  const cookieStore = await cookies()
  const token = cookieStore.get(env.JWT_COOKIE_NAME)?.value

  // For all routes, require authentication
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  headers.set("Authorization", `Bearer ${token}`)

  const body = await request.text()

  const response = await fetch(targetUrl, {
    method,
    headers,
    body: body || undefined,
  })

  if (response.status === 401) {
    // Clear cookie on 401
    const responseHeaders = new Headers()
    responseHeaders.set(
      "Set-Cookie",
      `${env.JWT_COOKIE_NAME}=; HttpOnly; Path=/; Max-Age=0`
    )

    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401, headers: responseHeaders }
    )
  }

  const data = await response.json()
  return NextResponse.json(data, { status: response.status })
}
