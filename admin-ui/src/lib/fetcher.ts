import { env } from "./env"

export class ApiError extends Error {
  constructor(message: string, public status: number, public data?: any) {
    super(message)
    this.name = "ApiError"
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: response.statusText }
    }

    throw new ApiError(
      errorData.message || `HTTP error! status: ${response.status}`,
      response.status,
      errorData
    )
  }

  return response.json()
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })

  return handleResponse<T>(response)
}

export async function apiPost<T>(endpoint: string, data?: any): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: data ? JSON.stringify(data) : undefined,
  })

  return handleResponse<T>(response)
}

export async function apiPut<T>(endpoint: string, data?: any): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: data ? JSON.stringify(data) : undefined,
  })

  return handleResponse<T>(response)
}

export async function apiDelete<T>(endpoint: string): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })

  return handleResponse<T>(response)
}

// API endpoints
export const apiEndpoints = {
  auth: {
    login: "/auth/login",
  },
  admin: {
    plans: "/admin/plans",
    plan: (code: string) => `/admin/plans/${code}`,
    addons: "/admin/addons",
    addon: (code: string) => `/admin/addons/${code}`,
    tenants: "/admin/tenants",
    tenant: (id: string) => `/admin/tenants/${id}`,
  },
  bootstrap: {
    sampleTenants: "/bootstrap/sample-tenants",
  },
} as const

