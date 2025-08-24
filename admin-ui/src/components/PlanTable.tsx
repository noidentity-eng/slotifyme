"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPut, apiEndpoints } from "@/lib/fetcher"
import { type Plan, type PlanUpdateData } from "@/lib/zod-schemas"
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
  Button,
  Input,
} from "@/lib/ui"
import { formatPrice } from "@/lib/utils"
import { useToast } from "@/components/Toast"
import { Edit, Save, X } from "lucide-react"

export function PlanTable() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [editingPlan, setEditingPlan] = useState<string | null>(null)
  const [editData, setEditData] = useState<PlanUpdateData>({})

  const { data: plans = [], isLoading } = useQuery({
    queryKey: ["plans"],
    queryFn: () => apiGet<Plan[]>(apiEndpoints.admin.plans),
  })

  const updatePlanMutation = useMutation({
    mutationFn: ({ code, data }: { code: string; data: PlanUpdateData }) =>
      apiPut(apiEndpoints.admin.plan(code), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] })
      setEditingPlan(null)
      setEditData({})
      toast({
        title: "Success",
        description: "Plan updated successfully",
      })
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update plan",
        variant: "destructive",
      })
    },
  })

  const handleEdit = (plan: Plan) => {
    setEditingPlan(plan.code)
    setEditData({
      limits: plan.limits,
      features: plan.features,
      overage_policy: plan.overage_policy,
      pricing_ref: plan.pricing_ref,
    })
  }

  const handleSave = (code: string) => {
    updatePlanMutation.mutate({ code, data: editData })
  }

  const handleCancel = () => {
    setEditingPlan(null)
    setEditData({})
  }

  const renderFeatureChips = (features: Record<string, boolean>) => {
    return Object.entries(features).map(([feature, enabled]) => (
      <span
        key={feature}
        className={`inline-block px-3 py-1 text-xs rounded-full mr-2 mb-2 font-medium ${
          enabled
            ? "bg-gradient-to-r from-[#b17a50] to-[#d4a574] text-white shadow-lg"
            : "bg-white/10 text-gray-400 border border-white/20"
        }`}
      >
        {feature.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
      </span>
    ))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 premium-gradient rounded-full mx-auto mb-4 animate-spin"></div>
          <p className="text-gray-400 text-lg">Loading premium plans...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
        <Table>
          <TableHeader>
            <TableRow className="border-white/10 bg-white/5">
              <TableHead className="text-[#b17a50] font-semibold">
                Plan
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Included Locations
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Included Stylists
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Preview Price
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Features
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Overage Policy
              </TableHead>
              <TableHead className="text-[#b17a50] font-semibold">
                Actions
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {plans.map((plan) => (
              <TableRow
                key={plan.code}
                className="border-white/10 hover:bg-white/5 transition-colors"
              >
                <TableCell>
                  <div>
                    <div className="font-semibold text-white">{plan.name}</div>
                    <div className="text-sm text-[#b17a50] font-medium">
                      {plan.code}
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-white">
                  {editingPlan === plan.code ? (
                    <Input
                      type="number"
                      className="bg-white/10 border-white/20 text-white placeholder-gray-400"
                      value={
                        editData.limits?.locations_included ||
                        plan.limits.locations_included
                      }
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          limits: {
                            locations_included: parseInt(e.target.value),
                            stylists_included:
                              editData.limits?.stylists_included ||
                              plan.limits.stylists_included,
                          },
                        })
                      }
                    />
                  ) : (
                    <span className="font-semibold">
                      {plan.limits.locations_included}
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-white">
                  {editingPlan === plan.code ? (
                    <Input
                      type="number"
                      className="bg-white/10 border-white/20 text-white placeholder-gray-400"
                      value={
                        editData.limits?.stylists_included ||
                        plan.limits.stylists_included
                      }
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          limits: {
                            locations_included:
                              editData.limits?.locations_included ||
                              plan.limits.locations_included,
                            stylists_included: parseInt(e.target.value),
                          },
                        })
                      }
                    />
                  ) : (
                    <span className="font-semibold">
                      {plan.limits.stylists_included}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <span className="text-[#b17a50] font-bold text-lg">
                    {plan.preview_amount_cents
                      ? formatPrice(plan.preview_amount_cents)
                      : "N/A"}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="max-w-xs">
                    {renderFeatureChips(plan.features)}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="text-sm text-gray-300">
                    <div className="mb-1">
                      <span className="text-[#b17a50]">Extra locations:</span>{" "}
                      <span
                        className={
                          plan.overage_policy.allow_extra_locations
                            ? "text-green-400"
                            : "text-red-400"
                        }
                      >
                        {plan.overage_policy.allow_extra_locations
                          ? "Yes"
                          : "No"}
                      </span>
                    </div>
                    <div>
                      <span className="text-[#b17a50]">Extra stylists:</span>{" "}
                      <span
                        className={
                          plan.overage_policy.allow_extra_stylists
                            ? "text-green-400"
                            : "text-red-400"
                        }
                      >
                        {plan.overage_policy.allow_extra_stylists
                          ? "Yes"
                          : "No"}
                      </span>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  {editingPlan === plan.code ? (
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        className="premium-button"
                        onClick={() => handleSave(plan.code)}
                        disabled={updatePlanMutation.isPending}
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        className="premium-button-outline"
                        onClick={handleCancel}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      className="premium-button-outline"
                      onClick={() => handleEdit(plan)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
