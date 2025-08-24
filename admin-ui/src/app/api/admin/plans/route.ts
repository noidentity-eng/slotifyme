import { NextRequest, NextResponse } from "next/server"

export async function GET() {
  // Mock plans data
  const plans = [
    {
      code: "silver",
      name: "Basic Plan",
      description: "Perfect for small businesses",
      price: 29.99,
      billing_cycle: "monthly",
      features: {
        locations_included: true,
        stylists_included: true,
        appointments_per_month: true,
        customer_support: true,
        basic_analytics: true,
        sms_notifications: false,
        email_marketing: false,
        advanced_analytics: false,
        custom_branding: false,
        api_access: false,
      },
      limits: {
        locations_included: 1,
        stylists_included: 5,
      },
      overage_policy: {
        allow_extra_locations: true,
        allow_extra_stylists: true,
      },
      preview_amount_cents: 2999,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
    {
      code: "gold",
      name: "Professional Plan",
      description: "Ideal for growing salons",
      price: 79.99,
      billing_cycle: "monthly",
      features: {
        locations_included: true,
        stylists_included: true,
        appointments_per_month: true,
        customer_support: true,
        basic_analytics: true,
        sms_notifications: true,
        email_marketing: true,
        advanced_analytics: false,
        custom_branding: false,
        api_access: false,
      },
      limits: {
        locations_included: 3,
        stylists_included: 15,
      },
      overage_policy: {
        allow_extra_locations: true,
        allow_extra_stylists: true,
      },
      preview_amount_cents: 7999,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
    {
      code: "platinum",
      name: "Enterprise Plan",
      description: "For large salon chains",
      price: 199.99,
      billing_cycle: "monthly",
      features: {
        locations_included: true,
        stylists_included: true,
        appointments_per_month: true,
        customer_support: true,
        basic_analytics: true,
        sms_notifications: true,
        email_marketing: true,
        advanced_analytics: true,
        custom_branding: true,
        api_access: true,
      },
      limits: {
        locations_included: 10,
        stylists_included: 50,
      },
      overage_policy: {
        allow_extra_locations: true,
        allow_extra_stylists: true,
      },
      preview_amount_cents: 19999,
      is_active: true,
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T00:00:00Z",
    },
  ]

  return NextResponse.json(plans)
}

export async function POST(request: NextRequest) {
  const body = await request.json()

  // Mock creating a new plan
  const newPlan = {
    code: body.code || "silver",
    ...body,
    overage_policy: body.overage_policy || {
      allow_extra_locations: true,
      allow_extra_stylists: true,
    },
    preview_amount_cents: body.preview_amount_cents || body.price * 100,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  return NextResponse.json(newPlan, { status: 201 })
}
