import { NextRequest, NextResponse } from "next/server"

// In-memory storage for mock data
let mockTenants = [
  {
    tenant_id: "1",
    name: "Beauty Haven Salon",
    slug: "beauty-haven",
    email: "contact@beautyhaven.com",
    phone: "+1-555-0123",
    status: "active",
    plan: "Professional Plan",
    locations_count: 1,
    created_at: "2024-01-15T00:00:00Z",
    updated_at: "2024-01-15T00:00:00Z",
  },
  {
    tenant_id: "2",
    name: "Elite Hair Studio",
    slug: "elite-hair",
    email: "info@elitehair.com",
    phone: "+1-555-0456",
    status: "active",
    plan: "Enterprise Plan",
    locations_count: 2,
    created_at: "2024-02-01T00:00:00Z",
    updated_at: "2024-02-01T00:00:00Z",
  },
  {
    tenant_id: "3",
    name: "Urban Cuts",
    slug: "urban-cuts",
    email: "hello@urbancuts.com",
    phone: "+1-555-0789",
    status: "active",
    plan: "Basic Plan",
    locations_count: 1,
    created_at: "2024-03-10T00:00:00Z",
    updated_at: "2024-03-10T00:00:00Z",
  },
]

export async function GET() {
  return NextResponse.json({ items: mockTenants })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  console.log("Creating tenant with data:", body)

  // Mock creating a new tenant with correct structure
  const newTenant = {
    tenant_id: (Math.floor(Math.random() * 1000) + 4).toString(),
    name: body.tenant?.name || "New Tenant",
    slug: body.tenant?.slug || "new-tenant",
    email: `${body.tenant?.slug || "new-tenant"}@slotifyme.com`,
    phone: body.location?.phone || "+1-555-0000",
    status: "active",
    plan: body.plan?.code || "basic",
    locations_count: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  // Add to in-memory storage
  mockTenants.push(newTenant)

  console.log("Created tenant:", newTenant)
  return NextResponse.json(newTenant, { status: 201 })
}
