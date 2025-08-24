"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost, apiEndpoints } from "@/lib/fetcher"
import { type Plan, type Addon, type TenantsResponse } from "@/lib/zod-schemas"
import { formatPrice } from "@/lib/utils"
import { useToast } from "@/components/Toast"
import {
  Users,
  Calendar,
  Plus,
  Settings,
  LogOut,
  User,
  CreditCard,
} from "lucide-react"

interface HomePagePlan {
  id: string
  name: string
  price: number
  duration: string
  features: string[]
  isActive: boolean
}

interface HomePageTenant {
  id: string
  name: string
  email: string
  phone: string
  plan: string
  status: "active" | "inactive" | "pending"
  joinDate: string
}

export default function HomePage() {
  const router = useRouter()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<"plans" | "tenants">("plans")
  const [showNewPlanForm, setShowNewPlanForm] = useState(false)
  const [showNewTenantForm, setShowNewTenantForm] = useState(false)

  // Fetch real data from APIs
  const { data: plansData = [], isLoading: plansLoading } = useQuery({
    queryKey: ["plans"],
    queryFn: () => apiGet<Plan[]>(apiEndpoints.admin.plans),
  })

  const { data: addonsData = [], isLoading: addonsLoading } = useQuery({
    queryKey: ["addons"],
    queryFn: () => apiGet<Addon[]>(apiEndpoints.admin.addons),
  })

  const { data: tenantsResponse, isLoading: tenantsLoading } = useQuery({
    queryKey: ["tenants"],
    queryFn: () => apiGet<TenantsResponse>(apiEndpoints.admin.tenants),
  })

  // Transform API data to match the home page format
  const plans: HomePagePlan[] = (plansData || []).map((plan) => ({
    id: plan.id?.toString() || plan.code || "unknown",
    name: plan.name,
    price: plan.preview_amount_cents
      ? plan.preview_amount_cents / 100
      : plan.price || 0,
    duration: "Monthly",
    features: Object.keys(plan.features || {}).filter(
      (key) => plan.features?.[key]
    ),
    isActive: true,
  }))

  // Handle both direct array and paginated response formats
  const tenantsData = Array.isArray(tenantsResponse)
    ? tenantsResponse
    : tenantsResponse?.items || []

  const tenants: HomePageTenant[] = tenantsData.map((tenant) => ({
    id: tenant.tenant_id || tenant.id?.toString() || "unknown",
    name: tenant.name,
    email: tenant.email || `${tenant.slug}@slotifyme.com`,
    phone: tenant.phone || "(555) 123-4567",
    plan: tenant.plan?.name || tenant.plan || "Basic",
    status: "active" as const,
    joinDate: tenant.created_at
      ? new Date(tenant.created_at).toISOString().split("T")[0]
      : new Date().toISOString().split("T")[0],
  }))

  const handleLogout = async () => {
    try {
      await fetch("/logout", { method: "POST" })
      router.push("/login")
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  const tabs = [
    {
      id: "plans",
      label: "Manage Plans",
      icon: CreditCard,
      description: "Manage service plans and pricing",
    },
    {
      id: "tenants",
      label: "Manage Tenants",
      icon: Users,
      description: "Manage customers and memberships",
    },
  ]

  const renderPlansContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Service Plans</h2>
          <p className="text-gray-400">
            Manage your barbershop service offerings
          </p>
        </div>
        <button
          onClick={() => router.push("/admin/plans")}
          className="premium-button flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Manage Plans</span>
        </button>
      </div>

      <div className="premium-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Plan Name
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Features
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-[#b17a50] uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {plans.map((plan) => (
                <tr
                  key={plan.id}
                  className="hover:bg-white/5 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="font-semibold text-white">{plan.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-2xl font-bold text-[#b17a50]">
                      ${plan.price}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-gray-300">{plan.duration}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      {plan.features.slice(0, 3).map((feature, index) => (
                        <div
                          key={index}
                          className="flex items-center space-x-2"
                        >
                          <div className="w-2 h-2 rounded-full bg-[#b17a50]"></div>
                          <span className="text-gray-300 text-sm">
                            {feature}
                          </span>
                        </div>
                      ))}
                      {plan.features.length > 3 && (
                        <div className="text-gray-500 text-sm">
                          +{plan.features.length - 3} more
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        plan.isActive
                          ? "bg-green-500/20 text-green-400 border border-green-500/30"
                          : "bg-gray-500/20 text-gray-400 border border-gray-500/30"
                      }`}
                    >
                      {plan.isActive ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Edit plan"
                        onClick={() => router.push("/admin/plans")}
                      >
                        ⚙️
                      </button>
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Archive plan"
                      >
                        📦
                      </button>
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title={
                          plan.isActive ? "Deactivate plan" : "Activate plan"
                        }
                      >
                        {plan.isActive ? "🔴" : "🟢"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderTenantsContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Customer Management
          </h2>
          <p className="text-gray-400">
            Manage your customers and their memberships
          </p>
        </div>
        <button
          onClick={() => router.push("/admin/tenants")}
          className="premium-button flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Manage Tenants</span>
        </button>
      </div>

      <div className="premium-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Join Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tenants.map((tenant) => (
                <tr
                  key={tenant.id}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center"
                        style={{
                          background:
                            "linear-gradient(to right, #b17a50, #c8855c)",
                        }}
                      >
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">
                          {tenant.name}
                        </div>
                        <div className="text-gray-500 text-sm">
                          ID: {tenant.id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-gray-900">{tenant.email}</div>
                    <div className="text-gray-500 text-sm">{tenant.phone}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className="px-3 py-1 rounded-full text-sm font-medium text-white"
                      style={{ backgroundColor: "#b17a50" }}
                    >
                      {tenant.plan}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        tenant.status === "active"
                          ? "bg-green-100 text-green-800"
                          : tenant.status === "pending"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {tenant.status.charAt(0).toUpperCase() +
                        tenant.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-900">
                    {new Date(tenant.joinDate).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Edit customer"
                        onClick={() => router.push("/admin/tenants")}
                      >
                        ⚙️
                      </button>
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Remove customer"
                      >
                        ❌
                      </button>
                      <button
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="View profile"
                      >
                        🔍
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  if (plansLoading || addonsLoading || tenantsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Premium Header */}
        <div className="text-center mb-12">
          <div className="inline-block p-2 mb-4">
            <div className="w-16 h-1 premium-gradient rounded-full mx-auto"></div>
          </div>
          <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
            Admin <span className="premium-text">Dashboard</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Welcome to your Slotifyme management console
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-1 border border-white/10">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as "plans" | "tenants")}
                  className={`px-6 py-3 rounded-lg transition-all duration-300 font-medium ${
                    activeTab === tab.id
                      ? "bg-gradient-to-r from-[#b17a50] to-[#d4a574] text-white shadow-lg"
                      : "text-gray-300 hover:text-white hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        {activeTab === "plans" ? renderPlansContent() : renderTenantsContent()}
      </div>
    </div>
  )
}
