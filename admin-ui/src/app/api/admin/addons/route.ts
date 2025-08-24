import { NextRequest, NextResponse } from "next/server"

export async function GET() {
  // Mock addons data
  const addons = [
    {
      code: "ai_booking",
      name: "AI Booking Assistant",
      description: "AI-powered booking and scheduling",
      price: 19.99,
      billing_cycle: "monthly",
      effect: {
        ai_booking: true,
      },
      preview_amount_cents: 1999,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
    {
      code: "variable_pricing",
      name: "Variable Pricing",
      description: "Dynamic pricing based on demand",
      price: 9.99,
      billing_cycle: "monthly",
      effect: {
        variable_pricing: true,
      },
      preview_amount_cents: 999,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
    {
      code: "value_pack",
      name: "Value Pack",
      description: "Bundle of premium features",
      price: 14.99,
      billing_cycle: "monthly",
      effect: {
        value_pack: true,
      },
      preview_amount_cents: 1499,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
  ]

  return NextResponse.json(addons)
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  // Mock creating a new addon
  const newAddon = {
    code: body.code || "ai_booking",
    ...body,
    effect: body.effect || {},
    preview_amount_cents: body.preview_amount_cents || body.price * 100,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  return NextResponse.json(newAddon, { status: 201 })
}
