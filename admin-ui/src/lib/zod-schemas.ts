import { z } from "zod"

// Login form schema
export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

export type LoginFormData = z.infer<typeof loginSchema>

// Plan schema
export const planSchema = z.object({
  code: z.enum(["silver", "gold", "platinum"]),
  name: z.string(),
  limits: z.object({
    locations_included: z.number(),
    stylists_included: z.number(),
  }),
  features: z.record(z.string(), z.boolean()),
  overage_policy: z.object({
    allow_extra_locations: z.boolean(),
    allow_extra_stylists: z.boolean(),
  }),
  pricing_ref: z.string().optional(),
  preview_amount_cents: z.number().optional(),
})

export type Plan = z.infer<typeof planSchema>

// Addon schema
export const addonSchema = z.object({
  code: z.enum(["ai_booking", "variable_pricing", "value_pack"]),
  name: z.string(),
  effect: z.record(z.string(), z.boolean()),
  pricing_ref: z.string().optional(),
  preview_amount_cents: z.number().optional(),
})

export type Addon = z.infer<typeof addonSchema>

// Tenant schema
export const tenantSchema = z.object({
  tenant_id: z.string(),
  name: z.string(),
  slug: z.string(),
  locations_count: z.number(),
  plan: z.string().optional(),
})

export type Tenant = z.infer<typeof tenantSchema>

// Tenants response schema
export const tenantsResponseSchema = z.object({
  items: z.array(tenantSchema),
  page: z.number(),
  total: z.number(),
})

export type TenantsResponse = z.infer<typeof tenantsResponseSchema>

// New tenant form schema
export const newTenantSchema = z.object({
  tenant: z.object({
    name: z.string().min(1, "Tenant name is required"),
    slug: z
      .string()
      .min(1, "Tenant slug is required")
      .regex(
        /^[a-z0-9-]+$/,
        "Slug must contain only lowercase letters, numbers, and hyphens"
      ),
  }),
  location: z.object({
    name: z.string().min(1, "Location name is required"),
    slug: z
      .string()
      .min(1, "Location slug is required")
      .regex(
        /^[a-z0-9-]+$/,
        "Slug must contain only lowercase letters, numbers, and hyphens"
      ),
    timezone: z.string().min(1, "Timezone is required"),
    phone: z.string().min(1, "Phone is required"),
    phone_public: z.boolean(),
  }),
  plan: z.object({
    code: z.enum(["silver", "gold", "platinum"]),
    addons: z.array(z.enum(["ai_booking", "variable_pricing", "value_pack"])),
    pricing_ref: z.string().optional(),
  }),
})

export type NewTenantFormData = z.infer<typeof newTenantSchema>

// Plan update schema
export const planUpdateSchema = z.object({
  limits: z
    .object({
      locations_included: z.number().min(0),
      stylists_included: z.number().min(0),
    })
    .optional(),
  features: z.record(z.string(), z.boolean()).optional(),
  overage_policy: z
    .object({
      allow_extra_locations: z.boolean(),
      allow_extra_stylists: z.boolean(),
    })
    .optional(),
  pricing_ref: z.string().optional(),
})

export type PlanUpdateData = z.infer<typeof planUpdateSchema>
